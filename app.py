import streamlit as st
import os
import re
import pandas as pd
import openai
import plotly.express as px
from tqdm import tqdm
from neo4j import GraphDatabase

# Set OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Neo4j Credentials
NEO4J_URI = "neo4j+s://e502785f.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "1PIyCt2xr4v07XGr0txGoxbA7-aLv54Pq2nHkQlg-q8"

# Initialize Streamlit app
st.set_page_config(page_title="Neo4j Query Generator", layout="wide")
st.title("🔍 Neo4j Query Generator with OpenAI")

class Neo4jClient:
    """Handles Neo4j database connections and queries."""
    
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def run_query(self, query):
        """Executes a Cypher query and returns results."""
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

# Initialize Neo4j Client
neo4j_client = Neo4jClient(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

def generate_cypher_query(user_prompt):
    """Generates a Cypher query from a user prompt using OpenAI."""
    prompt = f"""
    Generate a Cypher query to answer the following question based on a graph database of employee reviews:
    {user_prompt}

    The graph database has nodes: Review, Rating, Title.
    The Review node has properties: url, text, rating, details, title.
    The Rating node has property: rating.
    The Title node has property: title.
    The graph database has relationships: RATING_GIVEN, TITLE_ABOUT.

    Return only the Cypher query.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    cypher_query = response.choices[0].message.content.strip()

    # Ensure query is not empty
    if not cypher_query:
        st.error("⚠ OpenAI failed to generate a Cypher query. Please try again.")
        return None

    return cypher_query

def generate_response(results, user_prompt):
    """Generates a structured response from Neo4j query results using OpenAI."""
    if not results:
        return "No results found.", pd.DataFrame()

    formatted_results = "\n".join(str(record) for record in results)

    prompt = f"""
    Analyze the following Neo4j query results and the user's prompt:
    User Prompt: '{user_prompt}'
    Results: {formatted_results}

    The results represent reviews with url, text, rating, details, and title.

    1. Determine if a visualization (bar graph) is appropriate.
    2. If a bar graph is appropriate, generate Python code using plotly.express to create the graph.
    3. The code should extract ratings and titles from the results to create the graph.
    4. Return the python code for the plot, and then return the formatted results.
    5. If a visualization is not appropriate, just return the formatted results.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = response.choices[0].message.content.strip()

    # Extract ratings and titles safely
    ratings = [float(record.get('ra', {}).get('rating', 0)) for record in results]
    titles = [record.get('r', {}).get('title', "Unknown") for record in results]

    df = pd.DataFrame({'Title': titles, 'Rating': ratings})

    return analysis, df

# Query Section
st.subheader("💡 Ask a Question About the Neo4j Graph")
user_prompt = st.text_input("Enter your question:")

if st.button("🔍 Generate and Run Query"):
    if user_prompt:
        # Generate Cypher Query
        cypher_query = generate_cypher_query(user_prompt)
        
        if cypher_query:
            st.code(cypher_query, language="cypher")

            # Execute Query
            results = neo4j_client.run_query(cypher_query)

            # Format Results using GPT
            if results:
                formatted_response, df = generate_response(results, user_prompt)
                st.write("📝 **Formatted Answer:**")
                st.info(formatted_response)

                if not df.empty:
                    st.write("📋 **Query Results:**")
                    st.dataframe(df)

                    # Visualization (if applicable)
                    if "Rating" in df.columns:
                        st.write("📊 **Generated Visualization:**")
                        fig = px.bar(df, x="Title", y="Rating", title="Ratings per Title")
                        st.plotly_chart(fig)

            else:
                st.warning("⚠ No results found.")

# Close Neo4j connection
neo4j_client.close()