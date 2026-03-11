import importlib.util
import sys
import types
from pathlib import Path


def _load_search_module():
    generator_module = types.ModuleType("rag.prompts.generator")
    generator_module.relevant_chunks_with_toc = lambda *args, **kwargs: []

    rag_tokenizer_module = types.SimpleNamespace(
        tokenize=lambda text: text or "",
        fine_grained_tokenize=lambda text: text or "",
    )

    class _FulltextQueryer:
        def question(self, *args, **kwargs):
            return None, []

        def hybrid_similarity(self, *args, **kwargs):
            return [], [], []

        def token_similarity(self, *args, **kwargs):
            return []

        def rmWWW(self, text):
            return text

        def paragraph(self, *args, **kwargs):
            return None

    query_module = types.SimpleNamespace(FulltextQueryer=_FulltextQueryer)

    rag_nlp_module = types.ModuleType("rag.nlp")
    rag_nlp_module.rag_tokenizer = rag_tokenizer_module
    rag_nlp_module.query = query_module

    docstore_module = types.ModuleType("common.doc_store.doc_store_base")
    docstore_module.MatchDenseExpr = object
    docstore_module.FusionExpr = object
    docstore_module.OrderByExpr = object
    docstore_module.DocStoreConnection = object

    string_utils_module = types.ModuleType("common.string_utils")
    string_utils_module.remove_redundant_spaces = lambda text: text

    float_utils_module = types.ModuleType("common.float_utils")
    float_utils_module.get_float = float

    constants_module = types.ModuleType("common.constants")
    constants_module.PAGERANK_FLD = "pagerank_fea"
    constants_module.TAG_FLD = "tag_feas"

    settings_module = types.ModuleType("common.settings")
    settings_module.DOC_ENGINE_INFINITY = False

    common_module = types.ModuleType("common")
    common_module.settings = settings_module

    sys.modules["rag.prompts.generator"] = generator_module
    sys.modules["rag.nlp"] = rag_nlp_module
    sys.modules["common.doc_store.doc_store_base"] = docstore_module
    sys.modules["common.string_utils"] = string_utils_module
    sys.modules["common.float_utils"] = float_utils_module
    sys.modules["common.constants"] = constants_module
    sys.modules["common.settings"] = settings_module
    sys.modules["common"] = common_module

    module_path = Path("E:/AI数据集项目/boncflow/rag/nlp/search.py")
    spec = importlib.util.spec_from_file_location("search_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class _MissingParentDocStore:
    def get(self, *args, **kwargs):
        return None


def test_retrieval_by_children_keeps_children_when_parent_missing():
    search_module = _load_search_module()
    dealer = search_module.Dealer(_MissingParentDocStore())
    chunks = [
        {
            "chunk_id": "child-1",
            "content_ltks": "child chunk",
            "content_with_weight": "child content",
            "doc_id": "doc-1",
            "docnm_kwd": "doc name",
            "kb_id": "kb-1",
            "important_kwd": [],
            "image_id": "",
            "similarity": 0.91,
            "vector_similarity": 0.91,
            "term_similarity": 0.91,
            "vector": [0.1, 0.2],
            "positions": [],
            "doc_type_kwd": "text",
            "mom_id": "missing-parent",
            "q_2_vec": [0.1, 0.2],
        }
    ]

    result = dealer.retrieval_by_children(chunks, ["tenant-1"])

    assert len(result) == 1
    assert result[0]["chunk_id"] == "child-1"
    assert result[0]["content_with_weight"] == "child content"
