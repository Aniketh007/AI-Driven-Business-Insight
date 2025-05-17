import streamlit as st
import os
import re
import pandas as pd
import openai
import plotly.express as px
from tqdm import tqdm
from neo4j import GraphDatabase

# Neo4j Credentials
NEO4J_URI = "neo4j+s://455efffc.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "V-KFcjLA38WweEQGCC1u8zDpvPnmnYSMiOdGLV--tgo"

# Initialize Streamlit app
st.set_page_config(page_title="Neo4j Query Generator", layout="wide")
st.title("🔍 Neo4j Query Generator")

api_key=st.text_input("Enter your OpenAI API KEY")
client = openai.OpenAI(api_key=api_key)

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
    prompt = """
    Generate a Cypher query to answer the following question based on a graph database of Airbnb reviews:
    """ + str(user_prompt) + """

    The graph database has this EXACT structure:
    
    Nodes:
    1. Review
       - properties: id, date, comments
    2. Listing
       - properties: id
    3. Reviewer
       - properties: id, name

    Relationships:
    - (Reviewer)-[:WROTE]->(Review)
    - (Review)-[:ABOUT]->(Listing)

    RULES:
    1. Return ONLY the Cypher query with NO explanatory text
    2. Query MUST start with MATCH
    3. Query MUST include RETURN with aliases
    4. Use proper relationship directions (->)
    5. Include LIMIT for large result sets

    EXAMPLE RESPONSES:
    MATCH (r:Review) RETURN r.date as date, r.comments as comments ORDER BY date DESC LIMIT 5

    MATCH (rv:Reviewer)-[:WROTE]->(r:Review) WHERE rv.name CONTAINS "John" RETURN rv.name as reviewer, r.comments as comments

    MATCH (r:Review)-[:ABOUT]->(l:Listing {id: "2992450"}) RETURN r.date as date, r.comments as comments ORDER BY date DESC
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a Cypher query generator. Return ONLY the query with NO explanation or additional text."},
            {"role": "user", "content": prompt}
        ]
    )

    cypher_query = response.choices[0].message.content.strip()

    # Clean up the query
    def extract_valid_query(query_text):
        # Split into lines and remove empty ones
        lines = [line.strip() for line in query_text.split('\n') if line.strip()]
        
        # Look for lines starting with valid Cypher keywords
        valid_starters = ['MATCH', 'RETURN', 'WITH', 'CALL', 'CREATE', 'MERGE']
        for line in lines:
            if any(line.upper().startswith(keyword) for keyword in valid_starters):
                return line
        return None

    # Extract and validate the query
    cleaned_query = extract_valid_query(cypher_query)
    
    if not cleaned_query:
        st.error("⚠ Could not generate a valid Cypher query. Please try rephrasing your question.")
        return None

    # Ensure basic query structure
    if 'RETURN' not in cleaned_query.upper():
        st.error("⚠ Generated query is missing RETURN clause. Please try again.")
        return None

    if ' AS ' not in cleaned_query.upper():
        st.error("⚠ Generated query is missing column aliases. Please try again.")
        return None

    return cleaned_query

def generate_response(results, user_prompt):
    """Generates a structured response from Neo4j query results using OpenAI."""
    if not results:
        return "No results found.", pd.DataFrame()

    # Convert results to DataFrame first
    data = []
    for record in results:
        # Flatten the record dictionary
        flat_record = {}
        for key, value in record.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    flat_record[f"{key}_{k}"] = v
            else:
                flat_record[key] = value
        data.append(flat_record)
    
    df = pd.DataFrame(data)
    
    # Format the results for GPT
    formatted_results = df.to_string() if not df.empty else "No results found"

    prompt = """
    Analyze the following Neo4j query results about Airbnb reviews:
    User Question: '""" + str(user_prompt) + """'
    Results: """ + formatted_results + """

    Please provide:
    1. A clear, human-readable summary of the findings
    2. Any interesting patterns or insights in the reviews
    3. Relevant statistics (if available)
    4. Suggestions for further analysis

    If the results include dates, mention any temporal patterns.
    If the results include reviewer names, mention any patterns in reviewer behavior.
    If the results include comments, highlight any common themes or notable feedback.
    """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = response.choices[0].message.content.strip()

    return analysis, df

# Query Section
st.subheader("💡 Ask a Question About the Neo4j Graph")
st.info("A dataset of Airbnb reviews has been loaded into the Neo4j graph database.")
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
                # st.write("📝 **Formatted Answer:**")
                # st.info(formatted_response)

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
