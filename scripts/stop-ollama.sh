# Stop all model running on Ollama
ollama list | awk 'NR>1 {print $1}' | xargs -I {} sh -c 'echo "Stopping {}"; ollama stop {}'

# Stop Ollama service with Homebrew
brew services stop ollama