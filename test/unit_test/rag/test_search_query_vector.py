import importlib.util
import sys
import types
from pathlib import Path


class _MatchDenseExpr:
    def __init__(self, vector_column_name, embedding_data, data_type, metric, topk, extra_options):
        self.vector_column_name = vector_column_name
        self.embedding_data = embedding_data
        self.data_type = data_type
        self.metric = metric
        self.topk = topk
        self.extra_options = extra_options


class _FusionExpr:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class _OrderByExpr:
    def asc(self, *_args, **_kwargs):
        return None

    def desc(self, *_args, **_kwargs):
        return None


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
    docstore_module.MatchDenseExpr = _MatchDenseExpr
    docstore_module.FusionExpr = _FusionExpr
    docstore_module.OrderByExpr = _OrderByExpr
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
    spec = importlib.util.spec_from_file_location("search_vector_under_test", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class _DocStore:
    def __init__(self):
        self.last_match_exprs = None

    def search(self, src, highlight, filters, match_exprs, order_by, offset, limit, idx_names, kb_ids, rank_feature=None):
        self.last_match_exprs = match_exprs
        return {"total": 1}

    def get_total(self, _res):
        return 1

    def get_doc_ids(self, _res):
        return ["chunk-1"]

    def get_highlight(self, _res, _keywords, _field):
        return {}

    def get_aggregation(self, _res, _field):
        return []

    def get_fields(self, _res, _src):
        return {
            "chunk-1": {
                "docnm_kwd": "doc",
                "content_ltks": "chunk",
                "kb_id": "kb-1",
                "content_with_weight": "chunk content",
                "doc_id": "doc-1",
                "q_2_vec": [0.1, 0.2],
                "_score": 0.8,
            }
        }


def test_search_uses_provided_query_vector_without_encoding_text():
    search_module = _load_search_module()
    store = _DocStore()
    dealer = search_module.Dealer(store)

    class _EmbeddingModel:
        def encode_queries(self, _text):
            raise AssertionError("encode_queries should not be called when query_vector is provided")

    result = dealer.search(
        {
            "question": "",
            "query_vector": [0.3, 0.4],
            "page": 1,
            "size": 10,
            "similarity": 0.2,
        },
        "idx",
        ["kb-1"],
        emb_mdl=_EmbeddingModel(),
    )

    assert result.total == 1
    assert result.query_vector == [0.3, 0.4]
    assert len(store.last_match_exprs) == 1
    assert isinstance(store.last_match_exprs[0], _MatchDenseExpr)
    assert store.last_match_exprs[0].embedding_data == [0.3, 0.4]
