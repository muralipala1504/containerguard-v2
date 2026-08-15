import gradio as gr
import spaces

@spaces.GPU(duration=60)
def health_check():
    return "✅ ContainerGuard Backend API Running!"

demo = gr.Interface(
    fn=health_check,
    inputs=None,
    outputs="text",
    title="ContainerGuard Backend",
    description="K8s + Docker Monitoring API"
)

if __name__ == "__main__":
    demo.launch()
