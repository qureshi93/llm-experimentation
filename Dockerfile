FROM ollama/ollama

#Store model weight files in /models
ENV OLLAMA_MODELS /models

# Reduce logging verbosity
ENV OLLAMA_DEBUG false

#Never unload model weights from the GPU
ENV OLLAMA_KEEP_ALIVE -1

# Specify multiple models to include in the container
ENV MODELS "deepseek-r1:7b gemma3 llama3.3"

# Pull all the models
RUN ollama serve & sleep 5 && \
    for MODEL in $MODELS; do \
        ollama pull $MODEL; \
    done

#Stard Ollama
ENTRYPOINT ["ollama", "serve"]
