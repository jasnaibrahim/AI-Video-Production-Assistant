import streamlit as st
import requests
import json
from typing import Dict, Any
import plotly.graph_objects as go
import plotly.express as px

# Page config
st.set_page_config(
    page_title="AI Video Production Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E86AB;
        margin: 1rem 0;
        border-bottom: 2px solid #2E86AB;
        padding-bottom: 0.5rem;
    }
    .production-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #4ECDC4;
        margin: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
        transition: transform 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .metric-card:hover {
        transform: translateY(-2px);
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    .loading-step {
        animation: fadeInUp 0.5s ease-out;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        background: rgba(102, 126, 234, 0.1);
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Show initial loading if first time
    if 'app_initialized' not in st.session_state:
        with st.spinner("🎬 Initializing AI Video Production Assistant..."):
            import time
            time.sleep(0.5)  # Brief loading
            st.session_state.app_initialized = True
            st.rerun()

    # Header with animation
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3); animation: fadeInUp 0.8s ease-out;">
        <h1 style="margin: 0; font-size: 3rem;">🎬 AI Video Production Assistant</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">Transform your video idea into a complete production package!</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for input
    with st.sidebar:
        st.header("📝 Video Details")

        # Input form
        with st.form("video_idea_form"):
            idea = st.text_area(
                "Video Idea/Concept",
                placeholder="e.g., 'How to make perfect coffee at home using simple techniques'",
                height=100
            )

            platform = st.selectbox(
                "Platform",
                ["youtube", "instagram", "tiktok"],
                index=0
            )

            duration = st.selectbox(
                "Video Duration",
                ["1-3 minutes", "3-5 minutes", "5-10 minutes", "10+ minutes"],
                index=2,
                help="Choose the total length of your video. Longer videos will have more detailed scenes and content."
            )

            target_audience = st.selectbox(
                "Target Audience",
                ["general", "teens", "young adults", "professionals", "seniors"],
                index=0
            )

            tone = st.selectbox(
                "Video Tone",
                ["engaging", "educational", "funny", "professional", "casual"],
                index=0
            )

            submitted = st.form_submit_button("🚀 Generate Production Package", use_container_width=True)
    
    # Main content area
    if submitted and idea:
        # Beautiful loading experience
        show_beautiful_loading(idea, platform, duration, target_audience, tone)

    elif submitted and not idea:
        st.warning("Please enter a video idea to get started!")

    else:
        # Show instructions
        st.markdown("### 🎯 How to use:")
        st.markdown("1. **Enter your video idea** in the text area above")
        st.markdown("2. **Select your platform** (YouTube, Instagram, TikTok)")
        st.markdown("3. **Choose video duration** and target audience")
        st.markdown("4. **Click Generate** to create your production package")

        st.info("💡 **Tip:** Be specific with your video idea for better results. For example: 'How to make perfect coffee at home using a French press' instead of just 'coffee tutorial'")

        st.markdown("### ⚡ What you'll get:")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📝 Complete Screenplay**")
            st.markdown("- Scene-by-scene breakdown")
            st.markdown("- Exact timing for each scene")
            st.markdown("- Detailed action descriptions")

        with col2:
            st.markdown("**🎬 Professional Production**")
            st.markdown("- Shot list with camera angles")
            st.markdown("- Natural dialogue scripts")
            st.markdown("- Music recommendations")

        with col3:
            st.markdown("**📈 Marketing Strategy**")
            st.markdown("- SEO-optimized titles")
            st.markdown("- Thumbnail concepts")
            st.markdown("- Platform-specific posting strategy")

def show_beautiful_loading(idea, platform, duration, target_audience, tone):
    """Show a beautiful loading experience while generating content"""

    # Create loading container
    loading_container = st.container()

    with loading_container:
        # Header with animation
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h2 style="color: #ff6b6b; margin-bottom: 1rem;">
                🎬 Creating Your Video Production Package
            </h2>
            <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
                Generating professional content for: <strong>"{}"</strong>
            </p>
        </div>
        """.format(idea), unsafe_allow_html=True)

        # Progress steps with more detail and emojis
        progress_steps = [
            ("🎯", "Analyzing your video concept", "Understanding your idea and target audience"),
            ("📝", "Crafting SEO-optimized content", "Creating compelling title and hook"),
            ("🎬", "Writing detailed screenplay", "Scene-by-scene breakdown with timing"),
            ("📹", "Designing professional shots", "Camera angles and shot compositions"),
            ("💬", "Creating natural dialogue", "Engaging scripts and conversations"),
            ("🎵", "Selecting perfect audio", "Music and sound effect recommendations"),
            ("🖼️", "Generating thumbnail concepts", "Eye-catching visual ideas"),
            ("📱", f"Optimizing for {platform.title()}", "Platform-specific strategies"),
            ("📊", "Calculating engagement metrics", "Predicting views, likes, and shares"),
            ("✨", "Finalizing production package", "Putting it all together")
        ]

        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Create columns for stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Platform", platform.title(), "📱")
        with col2:
            st.metric("Duration", duration, "⏱️")
        with col3:
            st.metric("Audience", target_audience.title(), "👥")
        with col4:
            st.metric("Tone", tone.title(), "🎭")

        # Simulate progress with actual API call
        import time
        import threading

        # Container for the result
        result_container = st.empty()

        # Start API call in background
        production_data = None
        error_message = None

        def api_call():
            nonlocal production_data, error_message
            try:
                production_data = generate_production_package({
                    "idea": idea,
                    "platform": platform,
                    "duration": duration,
                    "target_audience": target_audience,
                    "tone": tone
                })
            except Exception as e:
                error_message = str(e)

        # Start the API call
        api_thread = threading.Thread(target=api_call)
        api_thread.start()

        # Show progress animation with beautiful steps
        for i, (emoji, title, description) in enumerate(progress_steps):
            progress = (i + 1) / len(progress_steps)
            progress_bar.progress(progress)

            # Beautiful step display
            status_text.markdown(f"""
            <div class="loading-step" style="text-align: center; padding: 1rem;
                 background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
                 border-radius: 12px; margin: 0.5rem 0;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{emoji}</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #333; margin-bottom: 0.25rem;">{title}</div>
                <div style="font-size: 0.9rem; color: #666; opacity: 0.8;">{description}</div>
            </div>
            """, unsafe_allow_html=True)

            time.sleep(1.2)  # Slightly longer for better UX

            # Check if API call is done
            if not api_thread.is_alive():
                break

        # Wait for API call to complete
        api_thread.join(timeout=30)  # 30 second timeout

        # Complete the progress
        progress_bar.progress(1.0)

        # Beautiful completion message
        status_text.markdown("""
        <div style="text-align: center; padding: 2rem;
             background: linear-gradient(135deg, #28a745, #20c997);
             color: white; border-radius: 15px; margin: 1rem 0;
             box-shadow: 0 8px 32px rgba(40, 167, 69, 0.3);
             animation: pulse 1s ease-in-out;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🎉</div>
            <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem;">Production Package Complete!</div>
            <div style="font-size: 1rem; opacity: 0.9;">Your professional video content is ready</div>
        </div>
        """, unsafe_allow_html=True)

        # Small delay for effect
        time.sleep(1.5)

        # Clear loading and show results
        loading_container.empty()

        if error_message:
            st.error(f"❌ Error generating content: {error_message}")
            st.info("💡 **Troubleshooting Tips:**\n- Check your internet connection\n- Try refreshing the page\n- Ensure the AI service is available")
        elif production_data:
            # Success animation and results
            st.balloons()
            st.success("🎬 **Success!** Your complete video production package is ready below!")
            display_production_package(production_data)
        else:
            st.error("❌ Failed to generate production package. Please try again.")
            st.info("💡 **What to try:**\n- Refresh the page and try again\n- Check if the AI service is running\n- Simplify your video idea if it's very complex")

def generate_production_package(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Call the FastAPI backend to generate production package"""
    try:
        # Try to call the actual API first
        try:
            response = requests.post("http://localhost:8000/generate-video-production", json=input_data, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                st.error("API server returned an error. Please check if the FastAPI server is running on localhost:8000")
                return None
        except requests.exceptions.RequestException:
            st.error("Cannot connect to API server. Please make sure the FastAPI server is running on localhost:8000")
            return None

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None



def display_production_package(data: Dict[str, Any]):
    """Display the complete production package"""

    # Title and Hook
    st.markdown('<div class="section-header">📺 Video Title & Hook</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="production-card"><h3>Title:</h3><p>{data["title"]}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="production-card"><h3>Hook (First 15 seconds):</h3><p>{data["hook"]}</p></div>', unsafe_allow_html=True)
    
    # Screenplay
    st.markdown('<div class="section-header">🎬 Scene-by-Scene Screenplay</div>', unsafe_allow_html=True)
    for scene in data["screenplay"]:
        with st.expander(f"Scene {scene['scene']}: {scene['description']} ({scene['timing']})"):
            st.write(f"**Action:** {scene['action']}")
    
    # Shot List and Camera Angles
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">📹 Shot List</div>', unsafe_allow_html=True)
        for shot in data["shot_list"]:
            st.markdown(f"""
            **Shot {shot['shot']}:** {shot['type']} ({shot['duration']})  
            *{shot['description']}*
            """)
    
    with col2:
        st.markdown('<div class="section-header">🎥 Camera Angles</div>', unsafe_allow_html=True)
        for angle in data["camera_angles"]:
            st.markdown(f"""
            **{angle['angle']}** - {angle['movement']}  
            *Purpose: {angle['purpose']}*
            """)
    
    # Dialogue
    st.markdown('<div class="section-header">💬 Key Dialogue</div>', unsafe_allow_html=True)
    for dialogue in data["dialogue"]:
        st.markdown(f"**{dialogue['timing']}** - {dialogue['speaker']}: *\"{dialogue['line']}\"*")
    
    # Production Elements
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">🎵 Music Suggestions</div>', unsafe_allow_html=True)
        for music in data["music_suggestions"]:
            st.markdown(f"• {music}")
    
    with col2:
        st.markdown('<div class="section-header">🖼️ Thumbnail Concepts</div>', unsafe_allow_html=True)
        for thumbnail in data["thumbnail_concepts"]:
            st.markdown(f"• {thumbnail}")
    
    # Posting Strategy
    st.markdown('<div class="section-header">📱 Posting Strategy</div>', unsafe_allow_html=True)
    strategy = data["posting_strategy"]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Best Time:** {strategy['best_time']}")
    with col2:
        st.markdown(f"**Hashtags:** {', '.join(strategy['hashtags'])}")
    with col3:
        st.markdown(f"**Description:** {strategy['description']}")
    
    # Download options
    st.markdown('<div class="section-header">📥 Export Options</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Download Script", use_container_width=True):
            script_content = create_script_download(data)
            st.download_button(
                label="Download Script as TXT",
                data=script_content,
                file_name="video_script.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("📋 Download Shot List", use_container_width=True):
            shot_list_content = create_shot_list_download(data)
            st.download_button(
                label="Download Shot List as TXT",
                data=shot_list_content,
                file_name="shot_list.txt",
                mime="text/plain"
            )
    
    with col3:
        if st.button("📊 Download Full Package", use_container_width=True):
            full_package = json.dumps(data, indent=2)
            st.download_button(
                label="Download as JSON",
                data=full_package,
                file_name="video_production_package.json",
                mime="application/json"
            )

def create_script_download(data: Dict[str, Any]) -> str:
    """Create downloadable script content"""
    script = f"""
VIDEO SCRIPT
===========

Title: {data['title']}

HOOK (0:00-0:15):
{data['hook']}

SCREENPLAY:
"""
    for scene in data['screenplay']:
        script += f"\nSCENE {scene['scene']} ({scene['timing']}): {scene['description']}\n"
        script += f"Action: {scene['action']}\n"
    
    script += "\n\nKEY DIALOGUE:\n"
    for dialogue in data['dialogue']:
        script += f"{dialogue['timing']} - {dialogue['speaker']}: \"{dialogue['line']}\"\n"
    
    return script

def create_shot_list_download(data: Dict[str, Any]) -> str:
    """Create downloadable shot list"""
    shot_list = "SHOT LIST\n=========\n\n"
    
    for shot in data['shot_list']:
        shot_list += f"Shot {shot['shot']}: {shot['type']} ({shot['duration']})\n"
        shot_list += f"Description: {shot['description']}\n\n"
    
    shot_list += "CAMERA ANGLES:\n"
    for angle in data['camera_angles']:
        shot_list += f"• {angle['angle']} - {angle['movement']} (Purpose: {angle['purpose']})\n"
    
    return shot_list



if __name__ == "__main__":
    main()
