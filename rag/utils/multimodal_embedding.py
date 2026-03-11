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

import io
import logging
from typing import Callable

import numpy as np
from PIL import Image


DEFAULT_IMAGE_VECTOR_WEIGHT = 0.65


def _call_storage_get(storage_get_func: Callable, bucket: str, name: str):
    try:
        return storage_get_func(bucket=bucket, fnm=name)
    except TypeError:
        return storage_get_func(bucket, name)


def _image_to_bytes(image) -> bytes | None:
    if not image:
        return None

    if isinstance(image, bytes):
        return image

    if not isinstance(image, Image.Image):
        return None

    img = image.convert("RGB") if image.mode in ("RGBA", "P") else image
    with io.BytesIO() as buf:
        img.save(buf, format="JPEG")
        return buf.getvalue()


def _load_chunk_image_bytes(chunk: dict, storage_get_func: Callable | None = None) -> bytes | None:
    image_bytes = _image_to_bytes(chunk.get("image"))
    if image_bytes:
        return image_bytes

    if not storage_get_func:
        return None

    image_id = chunk.get("img_id") or chunk.get("image_id")
    if not image_id or not isinstance(image_id, str):
        return None

    arr = image_id.split("-")
    if len(arr) != 2:
        return None

    try:
        blob = _call_storage_get(storage_get_func, arr[0], arr[1])
    except Exception:
        logging.exception("Load image bytes for %s failed", image_id)
        return None

    return blob if isinstance(blob, bytes) and blob else None


def supports_multimodal_embedding(embedding_model) -> bool:
    checker = getattr(embedding_model, "supports_image_embedding", None)
    if callable(checker):
        return bool(checker())

    mdl = getattr(embedding_model, "mdl", None)
    checker = getattr(mdl, "supports_image_documents", None)
    if callable(checker):
        return bool(checker())
    return False


def fuse_chunk_image_vectors(
    embedding_model,
    chunks: list[dict],
    text_vectors,
    storage_get_func: Callable | None = None,
    image_weight: float = DEFAULT_IMAGE_VECTOR_WEIGHT,
):
    if len(chunks) == 0:
        return np.array([]), 0, []

    vectors = np.asarray(text_vectors, dtype=np.float32).copy()
    if not supports_multimodal_embedding(embedding_model):
        return vectors, 0, []

    indices = []
    images = []
    for idx, chunk in enumerate(chunks):
        image_bytes = _load_chunk_image_bytes(chunk, storage_get_func=storage_get_func)
        if not image_bytes:
            continue
        indices.append(idx)
        images.append(image_bytes)

    if not images:
        return vectors, 0, []

    image_vectors, used_tokens = embedding_model.encode_image_documents(images)
    image_vectors = np.asarray(image_vectors, dtype=np.float32)
    if len(image_vectors) != len(indices):
        logging.warning(
            "Image embedding result size mismatch: images=%s vectors=%s",
            len(indices),
            len(image_vectors),
        )
        return vectors, used_tokens, []

    text_weight = 1.0 - image_weight
    for offset, idx in enumerate(indices):
        if vectors[idx].shape != image_vectors[offset].shape:
            logging.warning(
                "Skip multimodal fusion for chunk %s due to dimension mismatch: text=%s image=%s",
                idx,
                vectors[idx].shape,
                image_vectors[offset].shape,
            )
            continue
        merged = text_weight * vectors[idx] + image_weight * image_vectors[offset]
        norm = np.linalg.norm(merged)
        vectors[idx] = merged / norm if norm > 0 else merged

    return vectors, used_tokens, indices
