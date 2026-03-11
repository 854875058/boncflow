import io

import numpy as np
from PIL import Image

from rag.utils.multimodal_embedding import fuse_chunk_image_vectors


def _make_image_bytes(color=(255, 0, 0)):
    image = Image.new("RGB", (8, 8), color)
    with io.BytesIO() as buf:
        image.save(buf, format="JPEG")
        return buf.getvalue()


class _TextOnlyEmbeddingModel:
    def supports_image_embedding(self) -> bool:
        return False


class _MultimodalEmbeddingModel:
    def __init__(self, image_vector):
        self.image_vector = np.asarray(image_vector, dtype=np.float32)
        self.calls = 0

    def supports_image_embedding(self) -> bool:
        return True

    def encode_image_documents(self, images: list[bytes]):
        self.calls += 1
        return np.stack([self.image_vector for _ in images]), 9


def test_fuse_chunk_image_vectors_keeps_text_vectors_when_model_is_text_only():
    chunks = [{"image": _make_image_bytes()}]
    text_vectors = np.asarray([[1.0, 0.0]], dtype=np.float32)

    fused, used_tokens, fused_indices = fuse_chunk_image_vectors(
        _TextOnlyEmbeddingModel(),
        chunks,
        text_vectors,
    )

    np.testing.assert_allclose(fused, text_vectors)
    assert used_tokens == 0
    assert fused_indices == []


def test_fuse_chunk_image_vectors_blends_image_chunks():
    chunks = [
        {"image": _make_image_bytes()},
        {"content_with_weight": "text only"},
    ]
    text_vectors = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    model = _MultimodalEmbeddingModel([0.0, 1.0])

    fused, used_tokens, fused_indices = fuse_chunk_image_vectors(
        model,
        chunks,
        text_vectors,
        image_weight=0.5,
    )

    np.testing.assert_allclose(fused[0], np.asarray([0.70710677, 0.70710677], dtype=np.float32), rtol=1e-5)
    np.testing.assert_allclose(fused[1], text_vectors[1])
    assert used_tokens == 9
    assert fused_indices == [0]
    assert model.calls == 1


def test_fuse_chunk_image_vectors_loads_image_bytes_from_storage():
    chunks = [{"img_id": "bucket-object"}]
    text_vectors = np.asarray([[1.0, 0.0]], dtype=np.float32)
    model = _MultimodalEmbeddingModel([0.0, 1.0])

    def storage_get_func(bucket=None, fnm=None):
        assert bucket == "bucket"
        assert fnm == "object"
        return _make_image_bytes((0, 255, 0))

    fused, used_tokens, fused_indices = fuse_chunk_image_vectors(
        model,
        chunks,
        text_vectors,
        storage_get_func=storage_get_func,
        image_weight=0.5,
    )

    np.testing.assert_allclose(fused[0], np.asarray([0.70710677, 0.70710677], dtype=np.float32), rtol=1e-5)
    assert used_tokens == 9
    assert fused_indices == [0]
