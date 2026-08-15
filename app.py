import gradio as gr

demo = gr.Interface(
    fn=lambda: "ContainerGuard Backend API Running ✅",
    inputs=None,
    outputs="text",
    title="ContainerGuard Backend",
    description="K8s + Docker Monitoring"
)

if __name__ == "__main__":
    demo.launch()
