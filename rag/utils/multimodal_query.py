#
#  Copyright 2026 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import base64
import logging
from dataclasses import dataclass

import numpy as np

from api.db.services.llm_service import LLMBundle
from common.constants import LLMType
from rag.utils.multimodal_embedding import supports_multimodal_embedding


IMAGE_QUERY_VECTOR_WEIGHT = 0.65
IMAGE_QUERY_SUMMARY_PROMPT = (
    "请用简洁中文描述这张检索图片，保留对检索有帮助的信息：主体对象、场景、动作、颜色、文字、图表类型、布局和显著细节。"
    "不要编造信息，不要输出项目符号。"
)


@dataclass
class PreparedMultimodalQuery:
    question: str
    query_vector: list[float] | None
    media_summary: str = ""
    mode: str = "text"
    has_image: bool = False
    has_video: bool = False


def _decode_base64_payload(payload: str | None) -> bytes | None:
    if not payload or not isinstance(payload, str):
        return None

    encoded = payload.split(",", 1)[1] if payload.startswith("data:") and "," in payload else payload
    try:
        return base64.b64decode(encoded)
    except Exception:
        logging.exception("Decode multimodal query payload failed")
        return None


def _normalize_vector(vector) -> np.ndarray:
    arr = np.asarray(vector, dtype=np.float32)
    norm = np.linalg.norm(arr)
    return arr / norm if norm > 0 else arr


def _merge_query_vectors(
    text_vector,
    image_vector,
    image_weight: float = IMAGE_QUERY_VECTOR_WEIGHT,
) -> list[float]:
    merged = (1.0 - image_weight) * _normalize_vector(text_vector) + image_weight * _normalize_vector(image_vector)
    return _normalize_vector(merged).tolist()


async def _summarize_image_query(tenant_id: str, image_bytes: bytes) -> str:
    model = LLMBundle(tenant_id, LLMType.IMAGE2TEXT)
    return (model.describe_with_prompt(image_bytes, IMAGE_QUERY_SUMMARY_PROMPT) or "").strip()


async def _summarize_video_query(tenant_id: str, video_bytes: bytes, filename: str) -> str:
    model = LLMBundle(tenant_id, LLMType.IMAGE2TEXT)
    summary = await model.async_chat(
        system="",
        history=[],
        gen_conf={},
        video_bytes=video_bytes,
        filename=filename or "query.mp4",
    )
    return (summary or "").strip()


async def prepare_multimodal_query(
    tenant_id: str,
    embedding_model,
    question: str = "",
    image_base64: str | None = None,
    video_base64: str | None = None,
    media_filename: str = "",
    image_weight: float = IMAGE_QUERY_VECTOR_WEIGHT,
) -> PreparedMultimodalQuery:
    question = (question or "").strip()
    image_bytes = _decode_base64_payload(image_base64)
    video_bytes = _decode_base64_payload(video_base64)

    if image_bytes and video_bytes:
        raise ValueError("Only one query media file is supported at a time.")

    query_mode = "text"
    if image_bytes:
        query_mode = "image"
    elif video_bytes:
        query_mode = "video"

    image_vector = None
    media_summary = ""

    if image_bytes and supports_multimodal_embedding(embedding_model):
        try:
            image_vectors, _ = embedding_model.encode_image_documents([image_bytes])
            if len(image_vectors) > 0:
                image_vector = _normalize_vector(image_vectors[0])
        except Exception:
            logging.exception("Generate image query vector failed")

    needs_image_summary = bool(image_bytes) and (not question or image_vector is None)
    if needs_image_summary:
        try:
            media_summary = await _summarize_image_query(tenant_id, image_bytes)
        except Exception:
            logging.exception("Generate image query summary failed")

    if video_bytes:
        try:
            media_summary = await _summarize_video_query(tenant_id, video_bytes, media_filename)
        except Exception:
            logging.exception("Generate video query summary failed")

    query_parts = [question]
    if media_summary and media_summary not in query_parts:
        query_parts.append(media_summary)
    resolved_question = "\n".join(part for part in query_parts if part)

    text_vector = None
    if resolved_question:
        try:
            text_vector, _ = embedding_model.encode_queries(resolved_question)
            text_vector = _normalize_vector(text_vector)
        except Exception:
            logging.exception("Generate text query vector failed")

    query_vector = None
    if image_vector is not None and text_vector is not None:
        query_vector = _merge_query_vectors(text_vector, image_vector, image_weight=image_weight)
    elif image_vector is not None:
        query_vector = image_vector.tolist()
    elif text_vector is not None:
        query_vector = text_vector.tolist()

    return PreparedMultimodalQuery(
        question=resolved_question,
        query_vector=query_vector,
        media_summary=media_summary,
        mode=query_mode,
        has_image=bool(image_bytes),
        has_video=bool(video_bytes),
    )
