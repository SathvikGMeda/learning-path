import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import firestore
import json
import os
from datetime import datetime
import requests
import pandas as pd
import plotly.express as px

# Initialize services
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id')
vertexai.init(project=PROJECT_ID, location="us-central1")
model = GenerativeModel("gemini-1.5-flash")

# Streamlit page config
st.set_page_config(
    page_title="🎯 AI Learning Path Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .module-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sidebar .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Firestore
@st.cache_resource
def init_firestore():
    try:
        return firestore.Client()
    except Exception as e:
        st.error(f"Could not initialize Firestore: {e}")
        return None

def generate_learning_path_ai(profile):
    """Generate learning path using Vertex AI"""
    prompt = f"""
    Create a detailed, practical learning path for someone with:
    
    Current Skills: {profile.get('currentSkills', [])}
    Skill Levels: {profile.get('skillLevels', {})}
    Learning Goals: {profile.get('goals', [])}
    Learning Style: {profile.get('learningStyle', 'mixed')}
    Time Commitment: {profile.get('timeCommitment', '1-hour-daily')}
    
    Return ONLY valid JSON in this exact format:
    {{
        "title": "Personalized Learning Path Title",
        "description": "A comprehensive description of the learning journey",
        "estimatedDuration": "X months",
        "difficulty": "beginner/intermediate/advanced",
        "totalHours": 120,
        "modules": [
            {{
                "title": "Module Name",
                "duration": "X weeks", 
                "description": "Detailed module description",
                "skills": ["skill1", "skill2"],
                "learningObjectives": ["objective1", "objective2"],
                "resources": [
                    {{
                        "title": "Resource Name",
                        "type": "course/book/tutorial/project/video",
                        "provider": "Platform/Author",
                        "url": "https://example.com",
                        "difficulty": "beginner/intermediate/advanced",
                        "estimatedTime": "X hours",
                        "cost": "free/paid",
                        "description": "Why this resource is recommended"
                    }}
                ]
            }}
        ],
        "milestones": [
            {{
                "week": 2,
                "goal": "Complete Python fundamentals",
                "skills": ["python-basics"],
                "assessment": "Build a simple calculator app"
            }}
        ],
        "careerOutcomes": ["job_title1", "job_title2"],
        "estimatedSalaryRange": "$50,000 - $80,000"
    }}
    
    Focus on:
    - Free and affordable resources
    - Hands-on projects
    - Industry-relevant skills
    - Progressive difficulty
    - Real-world applications
    """
    
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text.strip())
    except Exception as e:
        st.error(f"AI Generation Error: {e}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 AI Learning Path Generator</h1>', unsafe_allow_html=True)
    st.markdown("### Generate personalized learning roadmaps powered by Google's Vertex AI")
    
    # Sidebar for user input
    with st.sidebar:
        st.header("👤 Create Your Learning Profile")
        
        # User ID
        user_id = st.text_input("👤 User ID", value="learner_" + str(hash(str(datetime.now())))[-6:], help="Unique identifier for your profile")
        
        # Skills Assessment
        st.subheader("🛠️ Current Skills")
        
        skill_categories = {
            "💻 Programming": [
                "Python", "JavaScript", "Java", "C++", "Go", "Rust", 
                "PHP", "C#", "Swift", "Kotlin", "TypeScript"
            ],
            "🔬 Data & AI": [
                "Data Analysis", "Machine Learning", "Deep Learning", 
                "SQL", "Statistics", "Data Visualization", "Big Data", "NLP"
            ],
            "🌐 Web Development": [
                "HTML/CSS", "React", "Vue.js", "Angular", "Node.js", 
                "Django", "Flask", "WordPress", "REST APIs"
            ],
            "☁️ Cloud & DevOps": [
                "AWS", "Google Cloud", "Azure", "Docker", "Kubernetes", 
                "CI/CD", "Terraform", "Linux", "Git"
            ],
            "🎨 Design & UX": [
                "UI/UX Design", "Graphic Design", "Product Design", 
                "Figma", "Adobe Creative Suite", "Prototyping"
            ],
            "💼 Business & Marketing": [
                "Project Management", "Digital Marketing", "SEO", 
                "Content Marketing", "Analytics", "Product Management"
            ]
        }
        
        current_skills = []
        skill_levels = {}
        
        for category, skills in skill_categories.items():
            with st.expander(f"{category} ({len(skills)} skills)"):
                for skill in skills:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        if st.checkbox(skill, key=f"skill_{skill}"):
                            skill_key = skill.lower().replace("/", "-").replace(" ", "-")
                            current_skills.append(skill_key)
                    
                    if skill.lower().replace("/", "-").replace(" ", "-") in current_skills:
                        with col2:
                            skill_levels[skill.lower().replace("/", "-").replace(" ", "-")] = st.select_slider(
                                "Level",
                                options=["Beginner", "Intermediate", "Advanced"],
                                value="Intermediate",
                                key=f"level_{skill}",
                                label_visibility="collapsed"
                            ).lower()
        
        # Learning Goals
        st.subheader("🎯 Learning Goals")
        goal_categories = {
            "Career Transitions": [
                "Become Data Scientist", "Become Web Developer", 
                "Become Software Engineer", "Become Cloud Architect",
                "Become Product Manager", "Become UX Designer"
            ],
            "Skill Enhancement": [
                "Learn Machine Learning", "Master Cloud Computing",
                "Get Cloud Certified", "Learn Mobile Development",
                "Master DevOps", "Learn Cybersecurity"
            ],
            "Business Goals": [
                "Start Freelancing", "Build a Startup",
                "Career Advancement", "Salary Increase",
                "Change Industries", "Remote Work Skills"
            ]
        }
        
        goals = []
        for category, goal_list in goal_categories.items():
            with st.expander(f"{category}"):
                for goal in goal_list:
                    if st.checkbox(goal, key=f"goal_{goal}"):
                        goals.append(goal.lower().replace(" ", "-"))
        
        # Learning Preferences
        st.subheader("⚙️ Learning Preferences")
        
        learning_style = st.selectbox(
            "🎓 Preferred Learning Style",
            ["Hands-on Projects", "Theoretical Study", "Mixed Approach", 
             "Video Tutorials", "Reading & Documentation", "Interactive Coding"]
        ).lower().replace(" ", "-")
        
        time_commitment = st.selectbox(
            "⏰ Time Commitment",
            ["30 minutes daily", "1 hour daily", "2 hours daily", 
             "3-4 hours daily", "Weekends only", "Flexible schedule"]
        ).lower().replace(" ", "-")
        
        budget_preference = st.selectbox(
            "💰 Budget Preference",
            ["Free resources only", "Under $50/month", "Under $100/month", 
             "No budget constraints"]
        ).lower().replace(" ", "-")
        
        # Generate Button
        if st.button("🚀 Generate My Learning Path", type="primary", use_container_width=True):
            if current_skills and goals:
                with st.spinner('🧠 AI is crafting your personalized learning journey...'):
                    profile_data = {
                        'currentSkills': current_skills,
                        'skillLevels': skill_levels,
                        'goals': goals,
                        'learningStyle': learning_style,
                        'timeCommitment': time_commitment,
                        'budgetPreference': budget_preference,
                        'created': datetime.now().isoformat()
                    }
                    
                    # Generate learning path
                    learning_path = generate_learning_path_ai(profile_data)
                    
                    if learning_path:
                        # Save to Firestore
                        db = init_firestore()
                        if db:
                            try:
                                learning_path['userId'] = user_id
                                learning_path['generated'] = firestore.SERVER_TIMESTAMP
                                learning_path['status'] = 'active'
                                learning_path['progress'] = 0
                                
                                path_ref = db.collection('learning_paths').document()
                                path_ref.set(learning_path)
                                
                                st.session_state[f'path_{user_id}'] = learning_path
                                st.session_state['show_path'] = True
                                st.success("✅ Your personalized learning path has been generated!")
                                st.rerun()
                                
                            except Exception as e:
                                st.warning(f"Could not save to database: {e}")
                                st.session_state[f'path_{user_id}'] = learning_path
                                st.session_state['show_path'] = True
                                st.rerun()
                        else:
                            st.session_state[f'path_{user_id}'] = learning_path
                            st.session_state['show_path'] = True
                            st.rerun()
            else:
                st.error("⚠️ Please select at least one skill and one goal to generate your learning path!")
    
    # Main content area
    if st.session_state.get('show_path') and st.session_state.get(f'path_{user_id}'):
        display_learning_path(st.session_state[f'path_{user_id}'])
    else:
        # Welcome screen
        display_welcome_screen()

def display_welcome_screen():
    """Display welcome screen with sample paths"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Personalized</h3>
            <p>AI analyzes your skills and creates a custom roadmap just for you</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🚀 Career-Focused</h3>
            <p>Paths designed to help you reach your professional goals</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>💰 Cost-Effective</h3>
            <p>Curated free and affordable resources to maximize your ROI</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sample learning paths
    st.header("🌟 Popular Learning Paths")
    
    sample_paths = [
        {
            "title": "🤖 AI/ML Engineer Path",
            "duration": "6-8 months",
            "skills": ["Python", "TensorFlow", "Data Science"],
            "description": "From Python basics to building production ML models"
        },
        {
            "title": "🌐 Full-Stack Web Developer",
            "duration": "4-6 months", 
            "skills": ["JavaScript", "React", "Node.js"],
            "description": "Build complete web applications from frontend to backend"
        },
        {
            "title": "☁️ Cloud Solutions Architect",
            "duration": "3-5 months",
            "skills": ["AWS/GCP", "DevOps", "Containers"],
            "description": "Design and deploy scalable cloud infrastructure"
        }
    ]
    
    cols = st.columns(len(sample_paths))
    for i, path in enumerate(sample_paths):
        with cols[i]:
            with st.container():
                st.markdown(f"### {path['title']}")
                st.markdown(f"**Duration:** {path['duration']}")
                st.markdown(f"**Skills:** {', '.join(path['skills'])}")
                st.markdown(path['description'])
                st.markdown("---")

def display_learning_path(path):
    """Display the generated learning path"""
    
    # Path header
    st.header(f"📋 {path['title']}")
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("📅 Duration", path['estimatedDuration'])
    with col2:
        st.metric("📊 Difficulty", path['difficulty'].title())
    with col3:
        st.metric("📚 Modules", len(path['modules']))
    with col4:
        st.metric("⏱️ Total Hours", f"{path.get('totalHours', 'N/A')}")
    with col5:
        st.metric("✅ Progress", f"{path.get('progress', 0)}%")
    
    # Path description
    st.markdown(f"**📝 Description:** {path['description']}")
    
    # Career outcomes
    if path.get('careerOutcomes'):
        st.markdown(f"**💼 Career Outcomes:** {', '.join(path['careerOutcomes'])}")
    
    if path.get('estimatedSalaryRange'):
        st.markdown(f"**💰 Estimated Salary Range:** {path['estimatedSalaryRange']}")
    
    st.markdown("---")
    
    # Learning modules
    st.subheader("📚 Learning Modules")
    
    for i, module in enumerate(path['modules'], 1):
        with st.expander(f"📖 Module {i}: {module['title']} ({module['duration']})", expanded=i==1):
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**📋 Description:** {module['description']}")
                
                if module.get('learningObjectives'):
                    st.markdown("**🎯 Learning Objectives:**")
                    for obj in module['learningObjectives']:
                        st.markdown(f"• {obj}")
                
                st.markdown(f"**🛠️ Skills to Learn:** {', '.join(module['skills'])}")
            
            with col2:
                # Progress tracking for module
                progress = st.slider(
                    f"Module {i} Progress",
                    0, 100, 0,
                    key=f"progress_module_{i}",
                    help=f"Track your progress through {module['title']}"
                )
                
                if st.button(f"✅ Mark Complete", key=f"complete_{i}"):
                    st.success(f"Module {i} marked as complete! 🎉")
            
            # Resources table
            if module.get('resources'):
                st.markdown("**📚 Recommended Resources:**")
                
                # Create DataFrame for better display
                resources_data = []
                for resource in module['resources']:
                    resources_data.append({
                        'Title': resource['title'],
                        'Type': resource['type'].title(),
                        'Provider': resource['provider'],
                        'Time': resource['estimatedTime'],
                        'Cost': resource.get('cost', 'N/A').title(),
                        'Difficulty': resource['difficulty'].title(),
                        'Description': resource.get('description', 'N/A')[:50] + '...' if resource.get('description') else 'N/A'
                    })
                
                resources_df = pd.DataFrame(resources_data)
                st.dataframe(resources_df, use_container_width=True, hide_index=True)
    
    # Milestones visualization
    if path.get('milestones'):
        st.subheader("🎯 Learning Milestones")
        
        milestone_data = []
        for milestone in path['milestones']:
            milestone_data.append({
                'Week': milestone['week'],
                'Goal': milestone['goal'],
                'Skills': ', '.join(milestone['skills']),
                'Assessment': milestone.get('assessment', 'Self-assessment')
            })
        
        milestone_df = pd.DataFrame(milestone_data)
        
        # Timeline chart
        fig = px.scatter(milestone_df, x='Week', y='Goal', 
                        title='Learning Timeline',
                        hover_data=['Skills', 'Assessment'])
        fig.update_traces(marker=dict(size=12, color='lightblue'))
        st.plotly_chart(fig, use_container_width=True)
        
        # Milestones table
        st.dataframe(milestone_df, use_container_width=True, hide_index=True)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Download Path (JSON)", use_container_width=True):
            st.download_button(
                "Download Learning Path",
                data=json.dumps(path, indent=2),
                file_name=f"learning_path_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🔄 Generate New Path", use_container_width=True):
            if 'show_path' in st.session_state:
                del st.session_state['show_path']
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("Analytics feature coming soon!")

if __name__ == "__main__":
    main()
