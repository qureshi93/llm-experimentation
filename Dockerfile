FROM ollama/ollama

#Store model weight files in /models
ENV OLLAMA_MODELS /models

# Reduce logging verbosity
ENV OLLAMA_DEBUG false

#Never unload model weights from the GPU
ENV OLLAMA_KEEP_ALIVE -1

#Store the model wieghts in the container image 
ENV MODEL deepseek-r1:7b
ENV MODEL gemma3
ENV MODEL llama3.3


RUN ollama serve & sleep 5 && ollama pull $MODEL

#Stard Ollama
ENTRYPOINT ["ollama", "serve"]
