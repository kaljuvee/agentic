import streamlit as st
import time
from graph.roast_agent import get_roast_questions

st.set_page_config(
    page_title="Comedy Roast Agent",
    page_icon="🎭",
    layout="centered"
)

st.title("🎭 Comedy Roast Question Generator")
st.markdown("""
This app generates hilarious roasting questions about a person. 
Enter a name, and the AI will search for information and create 5 funny roasting questions!
""")

# Input for name
name = st.text_input("Enter a name:", placeholder="e.g., Elon Musk, Taylor Swift, etc.")

if st.button("Generate Roast Questions", type="primary"):
    if name:
        with st.spinner(f"Searching for info about {name} and crafting roasts..."):
            # Call the roast agent
            start_time = time.time()
            roast_response = get_roast_questions(name)
            end_time = time.time()
            
            # Check if there was an error
            if roast_response.startswith("Error generating roast questions:"):
                st.error(roast_response)
            else:
                # Display the roasting questions
                st.subheader(f"Roast Results for {name}:")
                st.markdown(roast_response)
                
                # Show timing info
                st.caption(f"Generated in {end_time - start_time:.2f} seconds")
                
                # Add a fun element
                st.balloons()
    else:
        st.error("Please enter a name to generate roasting questions.")

st.markdown("---")
st.markdown("""
### How it works
1. The app searches for information about the person using DuckDuckGo
2. The AI analyzes the search results and identifies interesting facts
3. Based on this information, it creates 5 hilarious roasting questions
4. The questions are meant to be funny but not overly mean or inappropriate

### Tips
- Try celebrities, politicians, athletes, or other public figures
- The more well-known the person, the better the roasts will be
- You can use the questions for comedy nights, roast battles, or just for fun!
""")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using LangGraph and OpenAI")
