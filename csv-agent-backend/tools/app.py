# C:\Users\anvit\day4\csv-agent-backend\tools\app.py

from flask import Flask, request, jsonify, send_file
import os
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, ToolCall
from generate_summary import generate_csv_summary # This produces df.describe().to_string()
from visualize_csv import visualize_csv
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = "uploads"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

llm = ChatOpenAI(model="gpt-4", temperature=0.1) # Added temperature for more consistent output
# New prompt specifically for summarizing the descriptive statistics
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a data analysis assistant. Your task is to interpret the provided CSV descriptive statistics and give a concise, easy-to-understand textual summary. Highlight key features, distributions, potential outliers, or interesting insights."),
    ("human", "Here are the descriptive statistics of a CSV file:\n\n{descriptive_stats}\n\nPlease provide a clear, concise textual summary of this data.")
])

# Define the State for your graph
class CsvAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    file_path: str

# Define a function to call generate_csv_summary AND then prompt the LLM
def call_generate_csv_summary(state: CsvAgentState):
    file_path = state["file_path"]
    raw_summary_result = generate_csv_summary(file_path) # This is the df.describe().to_string()

    # Now, pass this raw summary to the LLM to get a textual summary
    llm_chain = summary_prompt | llm
    textual_summary = llm_chain.invoke({"descriptive_stats": raw_summary_result})
    
    # Return an AIMessage with the LLM's generated textual summary
    return {"messages": [AIMessage(content=f"Summary: {textual_summary.content}")]}

# Define a function to call visualize_csv
def call_visualize_csv(state: CsvAgentState):
    file_path = state["file_path"]
    plot_path = visualize_csv(file_path) # visualize_csv now returns the actual path if successful

    tool_call_data = {
        "name": "visualize_csv",
        "args": {"file_path": file_path},
        "id": "plot_tool_call_id_123"
    }
    # The content of AIMessage can describe the action or result
    return {"messages": [AIMessage(content=f"Plot generated and saved at: {plot_path}", tool_calls=[tool_call_data])]}


# Graph
graph = StateGraph(CsvAgentState)

graph.add_node("summarize", call_generate_csv_summary)
graph.add_node("visualize", call_visualize_csv)

graph.set_entry_point("summarize")
graph.add_edge("summarize", "visualize")
graph.add_edge("visualize", END)

app_graph = graph.compile()


@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    state = {
        "file_path": file_path,
        "messages": [HumanMessage(content=f"Process CSV file: {file.filename}")]
    }
    result = app_graph.invoke(state)

    summary_output = "No summary found."
    plot_url = "" # Initialize plot_url for frontend

    for message in result.get("messages", []):
        if isinstance(message, AIMessage):
            # The LLM's textual summary will be directly in the content from the "summarize" node
            if message.content.startswith("Summary:"):
                summary_output = message.content.replace("Summary: ", "")
            
            # The plot path will be in the content from the "visualize" node
            if message.content.startswith("Plot generated and saved at:"):
                # Assuming plot_path is the last part of the message content
                # e.g., "Plot generated and saved at: uploads\plot.png"
                returned_plot_path = message.content.split("Plot generated and saved at: ")[1].strip()
                # We only care about the filename for the /plot endpoint
                plot_url = "/plot" # The frontend will always request /plot

    return jsonify({
        "summary": summary_output,
        "image": plot_url if plot_url else "" # Only send image if a plot was successfully generated
    })

@app.route("/plot")
def get_plot():
    plot_file_path = os.path.join(UPLOAD_FOLDER, "plot.png")
    if os.path.exists(plot_file_path):
        return send_file(plot_file_path, mimetype='image/png')
    else:
        return jsonify({"error": "Plot not found"}), 404

@app.route('/')
def home():
    return "Backend is alive and kicking! "


if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)