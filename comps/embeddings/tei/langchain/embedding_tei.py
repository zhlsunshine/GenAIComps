# Copyright (C) 2024 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import os
import time
from typing import Union

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from comps import (
    CustomLogger,
    EmbedDoc,
    ServiceType,
    TextDoc,
    opea_microservices,
    register_microservice,
    register_statistics,
    statistics_dict,
)
from comps.cores.proto.api_protocol import (
    ChatCompletionRequest,
    EmbeddingRequest,
    EmbeddingResponse,
    EmbeddingResponseData,
)

logger = CustomLogger("embedding_tei_langchain")
logflag = os.getenv("LOGFLAG", False)


@register_microservice(
    name="opea_service@embedding_tei_langchain",
    service_type=ServiceType.EMBEDDING,
    endpoint="/v1/embeddings",
    host="0.0.0.0",
    port=6000,
)
@register_statistics(names=["opea_service@embedding_tei_langchain"])
async def embedding(
    input: Union[TextDoc, EmbeddingRequest, ChatCompletionRequest]
) -> Union[EmbedDoc, EmbeddingResponse, ChatCompletionRequest]:
    start = time.time()
    if logflag:
        logger.info(input)
    if isinstance(input, TextDoc):
        embed_vector = await embeddings.aembed_query(input.text)
        res = EmbedDoc(text=input.text, embedding=embed_vector)
    else:
        embed_vector = await embeddings.aembed_query(input.input)
        if input.dimensions is not None:
            embed_vector = embed_vector[: input.dimensions]

        if isinstance(input, ChatCompletionRequest):
            input.embedding = embed_vector
            # keep
            res = input
        if isinstance(input, EmbeddingRequest):
            # for standard openai embedding format
            res = EmbeddingResponse(data=[EmbeddingResponseData(index=0, embedding=embed_vector)])

    statistics_dict["opea_service@embedding_tei_langchain"].append_latency(time.time() - start, None)
    if logflag:
        logger.info(res)
    return res


if __name__ == "__main__":
    tei_embedding_endpoint = os.getenv("TEI_EMBEDDING_ENDPOINT", "http://localhost:8080")
    embeddings = HuggingFaceEndpointEmbeddings(model=tei_embedding_endpoint)
    logger.info("TEI Gaudi Embedding initialized.")
    opea_microservices["opea_service@embedding_tei_langchain"].start()
