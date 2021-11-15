from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2")


def vectorize(description: str):
    return model.encode(description)
