import streamlit as st
import time
from graph.roast_agent import get_roast_questions

# Translation dictionary
translations = {
    "en": {
        "page_title": "Comedy Roast Agent",
        "title": "🎭 Comedy Roast Question Generator",
        "description": "This app generates hilarious roasting questions about a person. Enter a name, and the AI will search for information and create 5 funny roasting questions!",
        "name_input": "Enter a name:",
        "name_placeholder": "e.g., Elon Musk, Taylor Swift, etc.",
        "button_text": "Generate Roast Questions",
        "loading_text": "Searching for info about {name} and crafting roasts...",
        "results_title": "Roast Results for {name}:",
        "generated_in": "Generated in {time:.2f} seconds",
        "error_message": "Please enter a name to generate roasting questions.",
        "how_it_works_title": "How it works",
        "how_it_works_1": "The app searches for information about the person using DuckDuckGo",
        "how_it_works_2": "The AI analyzes the search results and identifies interesting facts",
        "how_it_works_3": "Based on this information, it creates 5 hilarious roasting questions",
        "how_it_works_4": "The questions are meant to be funny but not overly mean or inappropriate",
        "tips_title": "Tips",
        "tips_1": "Try celebrities, politicians, athletes, or other public figures",
        "tips_2": "The more well-known the person, the better the roasts will be",
        "tips_3": "You can use the questions for comedy nights, roast battles, or just for fun!",
        "footer": "Built with ❤️ using LangGraph and OpenAI",
        "language_selector": "Language:"
    },
    "et": {
        "page_title": "Komöödia Röstimise Agent",
        "title": "🎭 Komöödia Röstimise Küsimuste Generaator",
        "description": "See rakendus genereerib naljakaid röstimisküsimusi inimese kohta. Sisesta nimi ja tehisintellekt otsib infot ning loob 5 naljakat röstimisküsimust!",
        "name_input": "Sisesta nimi:",
        "name_placeholder": "nt Elon Musk, Taylor Swift jne",
        "button_text": "Genereeri Röstimisküsimused",
        "loading_text": "Otsin infot {name} kohta ja koostan röstimisküsimusi...",
        "results_title": "Röstimistulemused {name} kohta:",
        "generated_in": "Genereeritud {time:.2f} sekundiga",
        "error_message": "Palun sisesta nimi, et genereerida röstimisküsimusi.",
        "how_it_works_title": "Kuidas see töötab",
        "how_it_works_1": "Rakendus otsib infot inimese kohta DuckDuckGo abil",
        "how_it_works_2": "Tehisintellekt analüüsib otsingutulemusi ja tuvastab huvitavaid fakte",
        "how_it_works_3": "Selle info põhjal loob ta 5 naljakat röstimisküsimust",
        "how_it_works_4": "Küsimused on mõeldud olema naljakad, kuid mitte liiga õelad või ebasobivad",
        "tips_title": "Näpunäited",
        "tips_1": "Proovi kuulsusi, poliitikuid, sportlasi või teisi avaliku elu tegelasi",
        "tips_2": "Mida tuntum on inimene, seda paremad on röstimisküsimused",
        "tips_3": "Saad kasutada küsimusi komöödiaõhtutel, röstimislahingutes või lihtsalt lõbuks!",
        "footer": "Loodud ❤️-ga kasutades LangGraph'i ja OpenAI'd",
        "language_selector": "Keel:"
    }
}

# Initialize session state for language if it doesn't exist
if 'language' not in st.session_state:
    st.session_state.language = "et"  # Default to Estonian

def get_text(key):
    return translations[st.session_state.language][key]

# Set page config
st.set_page_config(
    page_title=get_text("page_title"),
    page_icon="🎭",
    layout="centered"
)

# Language selector in sidebar
with st.sidebar:
    selected_language = st.radio(
        get_text("language_selector"),
        options=["Eesti keel", "English"],
        index=0 if st.session_state.language == "et" else 1
    )
    
    # Update language based on selection
    if selected_language == "Eesti keel" and st.session_state.language != "et":
        st.session_state.language = "et"
        st.rerun()
    elif selected_language == "English" and st.session_state.language != "en":
        st.session_state.language = "en"
        st.rerun()

# Main content
st.title(get_text("title"))
st.markdown(get_text("description"))

# Input for name
name = st.text_input(get_text("name_input"), placeholder=get_text("name_placeholder"))

if st.button(get_text("button_text"), type="primary"):
    if name:
        with st.spinner(get_text("loading_text").format(name=name)):
            # Call the roast agent with the current language
            start_time = time.time()
            roast_response = get_roast_questions(name, st.session_state.language)
            end_time = time.time()
            
            # Check if there was an error
            if roast_response.startswith("Error generating roast questions:"):
                st.error(roast_response)
            else:
                # Display the roasting questions
                st.subheader(get_text("results_title").format(name=name))
                st.markdown(roast_response)
                
                # Show timing info
                st.caption(get_text("generated_in").format(time=end_time - start_time))
                
                # Add a fun element
                st.balloons()
    else:
        st.error(get_text("error_message"))

st.markdown("---")
st.markdown(f"### {get_text('how_it_works_title')}")
st.markdown(f"1. {get_text('how_it_works_1')}")
st.markdown(f"2. {get_text('how_it_works_2')}")
st.markdown(f"3. {get_text('how_it_works_3')}")
st.markdown(f"4. {get_text('how_it_works_4')}")

st.markdown(f"### {get_text('tips_title')}")
st.markdown(f"- {get_text('tips_1')}")
st.markdown(f"- {get_text('tips_2')}")
st.markdown(f"- {get_text('tips_3')}")

# Footer
st.markdown("---")
st.markdown(get_text("footer"))
