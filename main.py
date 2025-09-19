from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = FastAPI(title="AI Video Production Assistant", version="1.0.0")

# Configure OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class VideoIdeaInput(BaseModel):
    idea: str
    platform: str = "youtube"  # youtube, instagram, tiktok
    duration: str = "5-10 minutes"  # short, medium, long
    target_audience: str = "general"
    tone: str = "engaging"  # casual, professional, funny, educational

class VideoProductionOutput(BaseModel):
    title: str
    hook: str
    screenplay: List[Dict]
    shot_list: List[Dict]
    dialogue: List[Dict]
    camera_angles: List[Dict]
    music_suggestions: List[str]
    thumbnail_concepts: List[str]
    posting_strategy: Dict
    estimated_engagement: Dict

@app.post("/generate-video-production", response_model=VideoProductionOutput)
async def generate_video_production(input_data: VideoIdeaInput):
    try:
        # Generate complete video production package with timeout protection
        production_data = await create_complete_production_fast(input_data)
        return production_data
    except Exception as e:
        # If AI generation fails, raise the error
        print(f"AI generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

async def create_complete_production_fast(input_data: VideoIdeaInput) -> VideoProductionOutput:
    """Generate complete video production package using a single efficient OpenAI call"""

    # Create comprehensive prompt for video production
    # Convert duration to specific timing requirements
    duration_mapping = {
        "1-3 minutes": {"total_time": "3:00", "scenes": 4, "example_timing": "0:00-0:15, 0:15-1:30, 1:30-2:30, 2:30-3:00"},
        "3-5 minutes": {"total_time": "5:00", "scenes": 5, "example_timing": "0:00-0:15, 0:15-1:30, 1:30-3:00, 3:00-4:30, 4:30-5:00"},
        "5-10 minutes": {"total_time": "8:00", "scenes": 6, "example_timing": "0:00-0:30, 0:30-2:00, 2:00-4:00, 4:00-6:00, 6:00-7:30, 7:30-8:00"},
        "10+ minutes": {"total_time": "12:00", "scenes": 7, "example_timing": "0:00-0:30, 0:30-2:30, 2:30-5:00, 5:00-7:30, 7:30-10:00, 10:00-11:30, 11:30-12:00"}
    }

    duration_info = duration_mapping.get(input_data.duration, duration_mapping["5-10 minutes"])

    prompt = f"""
    Create a complete video production package for the following idea:

    Idea: {input_data.idea}
    Platform: {input_data.platform}
    Duration: {input_data.duration} (TOTAL VIDEO LENGTH: {duration_info['total_time']})
    Target Audience: {input_data.target_audience}
    Tone: {input_data.tone}

    CRITICAL: The video must be exactly {duration_info['total_time']} long. Create {duration_info['scenes']} scenes that add up to this total duration.

    Generate a comprehensive production package in JSON format with these exact keys:
    {{
        "title": "SEO-optimized title for {input_data.platform}",
        "hook": "Compelling 15-second opening hook",
        "screenplay": [
            {{"scene": 1, "timing": "0:00-0:15", "description": "Opening", "action": "Detailed action"}},
            {{"scene": 2, "timing": "0:15-1:30", "description": "Main content part 1", "action": "Detailed action"}},
            {{"scene": 3, "timing": "1:30-3:00", "description": "Main content part 2", "action": "Detailed action"}},
            {{"scene": 4, "timing": "3:00-4:30", "description": "Main content part 3", "action": "Detailed action"}},
            {{"scene": 5, "timing": "4:30-{duration_info['total_time']}", "description": "Conclusion", "action": "Detailed action"}}
        ],
        "shot_list": [
            {{"shot": 1, "type": "Wide shot", "description": "Description", "duration": "30 seconds", "purpose": "Establish scene"}}
        ],
        "dialogue": [
            {{"speaker": "Host", "line": "Dialogue text", "timing": "0:00-0:05"}}
        ],
        "camera_angles": [
            {{"angle": "Eye level", "movement": "Static", "purpose": "Natural perspective", "timing": "Opening"}}
        ],
        "music_suggestions": ["Upbeat background music", "Transition sound effects"],
        "thumbnail_concepts": ["Eye-catching concept 1", "Concept 2"],
        "posting_strategy": {{
            "best_time": "Peak hours for {input_data.platform}",
            "hashtags": ["#relevant", "#hashtags"],
            "description": "Engaging description",
            "engagement_tactics": ["Call to action", "Question for comments"]
        }},
        "estimated_engagement": {{
            "views": "Estimated view count",
            "likes": "Estimated likes",
            "shares": "Estimated shares",
            "comments": "Estimated comments"
        }}
    }}

    IMPORTANT:
    - Create exactly {duration_info['scenes']} scenes that total {duration_info['total_time']}
    - Example timing structure: {duration_info['example_timing']}
    - Each scene should be substantial and detailed for the {input_data.duration} duration
    - Make it detailed, platform-specific, and actionable.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert video production assistant. Always respond with valid JSON in the exact format requested."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.7
        )

        # Parse the JSON response
        import json
        content = response.choices[0].message.content

        # Clean up the response if it has markdown formatting
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()

        production_data = json.loads(content)

        # Validate and return structured output
        return VideoProductionOutput(
            title=production_data.get("title", f"Amazing {input_data.idea} Guide"),
            hook=production_data.get("hook", f"Want to learn about {input_data.idea}? Here's everything you need to know!"),
            screenplay=production_data.get("screenplay", []),
            shot_list=production_data.get("shot_list", []),
            dialogue=production_data.get("dialogue", []),
            camera_angles=production_data.get("camera_angles", []),
            music_suggestions=production_data.get("music_suggestions", []),
            thumbnail_concepts=production_data.get("thumbnail_concepts", []),
            posting_strategy=production_data.get("posting_strategy", {}),
            estimated_engagement=production_data.get("estimated_engagement", {})
        )

    except Exception as e:
        print(f"Fast generation failed: {str(e)}")
        raise e



async def create_complete_production(input_data: VideoIdeaInput) -> VideoProductionOutput:
    """Generate complete video production package using OpenAI"""
    
    # Create comprehensive prompt for video production
    prompt = f"""
    Create a complete video production package for the following idea:
    
    Idea: {input_data.idea}
    Platform: {input_data.platform}
    Duration: {input_data.duration}
    Target Audience: {input_data.target_audience}
    Tone: {input_data.tone}
    
    Generate a comprehensive production package including:
    
    1. TITLE: Catchy, SEO-optimized title
    2. HOOK: Compelling first 15 seconds to grab attention
    3. SCREENPLAY: Scene-by-scene breakdown with timing
    4. SHOT_LIST: Detailed camera shots and angles
    5. DIALOGUE: Complete script with natural conversations
    6. CAMERA_ANGLES: Specific camera movements and positions
    7. MUSIC_SUGGESTIONS: Background music recommendations
    8. THUMBNAIL_CONCEPTS: Eye-catching thumbnail ideas
    9. POSTING_STRATEGY: Best times, hashtags, descriptions
    10. ESTIMATED_ENGAGEMENT: Predicted views, likes, shares
    
    Format the response as a detailed JSON structure.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert video production assistant who creates comprehensive production packages for content creators. Always respond with detailed, actionable content in JSON format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        # Parse the response and structure it
        content = response.choices[0].message.content
        
        # Generate structured output
        production_output = await structure_production_output(content, input_data)
        return production_output
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating production: {str(e)}")

async def structure_production_output(ai_content: str, input_data: VideoIdeaInput) -> VideoProductionOutput:
    """Structure the AI output into our defined format with enhanced AI generation"""

    # Generate title with platform optimization
    title_prompt = f"""Create a catchy, SEO-optimized title for {input_data.platform} about: {input_data.idea}

    Platform: {input_data.platform}
    Target audience: {input_data.target_audience}
    Tone: {input_data.tone}

    Make it clickable, include power words, and optimize for {input_data.platform} algorithm.
    """

    title_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": title_prompt}],
        max_tokens=100
    )
    title = title_response.choices[0].message.content.strip()

    # Generate compelling hook
    hook_prompt = f"""Create a compelling 15-second hook for a {input_data.platform} video about: {input_data.idea}

    Requirements:
    - Grab attention in first 3 seconds
    - Create curiosity gap
    - Match {input_data.tone} tone
    - Target {input_data.target_audience} audience
    - Include pattern interrupt or surprising statement

    Write the exact words the creator should say.
    """

    hook_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": hook_prompt}],
        max_tokens=200
    )
    hook = hook_response.choices[0].message.content.strip()

    # Convert duration to specific timing requirements for screenplay
    duration_mapping = {
        "1-3 minutes": {"total_time": "3:00", "scenes": 4, "scene_timings": ["0:00-0:15", "0:15-1:30", "1:30-2:30", "2:30-3:00"]},
        "3-5 minutes": {"total_time": "5:00", "scenes": 5, "scene_timings": ["0:00-0:15", "0:15-1:30", "1:30-3:00", "3:00-4:30", "4:30-5:00"]},
        "5-10 minutes": {"total_time": "8:00", "scenes": 6, "scene_timings": ["0:00-0:30", "0:30-2:00", "2:00-4:00", "4:00-6:00", "6:00-7:30", "7:30-8:00"]},
        "10+ minutes": {"total_time": "12:00", "scenes": 7, "scene_timings": ["0:00-0:30", "0:30-2:30", "2:30-5:00", "5:00-7:30", "7:30-10:00", "10:00-11:30", "11:30-12:00"]}
    }

    duration_info = duration_mapping.get(input_data.duration, duration_mapping["5-10 minutes"])

    # Generate detailed screenplay using AI
    screenplay_prompt = f"""Create a detailed scene-by-scene screenplay for: {input_data.idea}

    Duration: {input_data.duration} (TOTAL LENGTH: {duration_info['total_time']})
    Platform: {input_data.platform}
    Tone: {input_data.tone}
    Target audience: {input_data.target_audience}

    CRITICAL: Create exactly {duration_info['scenes']} scenes that total {duration_info['total_time']} in length.
    Use these exact timings: {', '.join(duration_info['scene_timings'])}

    Create {duration_info['scenes']} scenes with:
    - Scene number (1 to {duration_info['scenes']})
    - Specific timing from the list above
    - Scene description/title
    - Detailed action description (substantial content for each time segment)

    Format as JSON array with keys: scene, timing, description, action
    Make it engaging and optimized for {input_data.platform}.
    Each scene should have enough content to fill its allocated time slot.
    """

    try:
        screenplay_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional screenwriter. Create detailed, engaging screenplays for video content. Always respond with valid JSON."},
                {"role": "user", "content": screenplay_prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )

        try:
            import json
            screenplay = json.loads(screenplay_response.choices[0].message.content)
        except Exception as e:
            print(f"Failed to parse screenplay JSON: {e}")
            raise Exception("Failed to generate screenplay")
    except Exception as e:
        print(f"Failed to generate screenplay: {e}")
        raise Exception("Failed to generate screenplay")

    # Generate comprehensive shot list
    shot_list = await generate_shot_list(input_data)

    # Generate dialogue
    dialogue = await generate_dialogue(input_data, screenplay)

    # Generate camera angles
    camera_angles = await generate_camera_angles(input_data)

    # Generate music suggestions
    music_suggestions = await generate_music_suggestions(input_data)

    # Generate thumbnail concepts
    thumbnail_concepts = await generate_thumbnail_concepts(input_data)

    # Generate posting strategy
    posting_strategy = await generate_posting_strategy(input_data)

    # Generate engagement estimates
    estimated_engagement = await generate_engagement_estimates(input_data)

    return VideoProductionOutput(
        title=title,
        hook=hook,
        screenplay=screenplay,
        shot_list=shot_list,
        dialogue=dialogue,
        camera_angles=camera_angles,
        music_suggestions=music_suggestions,
        thumbnail_concepts=thumbnail_concepts,
        posting_strategy=posting_strategy,
        estimated_engagement=estimated_engagement
    )

async def generate_shot_list(input_data: VideoIdeaInput) -> List[Dict]:
    """Generate detailed shot list using AI"""
    prompt = f"""Create a detailed shot list for a {input_data.platform} video about: {input_data.idea}

    Duration: {input_data.duration}
    Tone: {input_data.tone}
    Target audience: {input_data.target_audience}

    Generate 5-7 specific shots with:
    - Shot number
    - Shot type (close-up, medium, wide, over-shoulder, B-roll, etc.)
    - Detailed description of what's being filmed
    - Duration for each shot
    - Purpose/reason for the shot

    Format as a JSON array of objects with keys: shot, type, description, duration, purpose
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional cinematographer. Generate detailed, specific shot lists for video production. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )

        # Try to parse JSON response
        try:
            import json
            shots = json.loads(response.choices[0].message.content)
            return shots
        except Exception as e:
            print(f"Failed to parse shot list JSON: {e}")
            raise Exception("Failed to generate shot list")

    except Exception as e:
        print(f"Failed to generate shot list: {e}")
        raise Exception("Failed to generate shot list")

async def generate_dialogue(input_data: VideoIdeaInput, screenplay: List[Dict]) -> List[Dict]:
    """Generate natural dialogue for the video using AI"""
    prompt = f"""Write natural, engaging dialogue for a {input_data.platform} video about: {input_data.idea}

    Tone: {input_data.tone}
    Target audience: {input_data.target_audience}
    Duration: {input_data.duration}

    Create 4-6 key dialogue lines that:
    - Sound conversational and authentic
    - Match the {input_data.tone} tone
    - Are appropriate for {input_data.platform}
    - Include specific timing (e.g., "0:00-0:05")
    - Have natural transitions and flow

    Format as JSON array with keys: speaker, line, timing
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional scriptwriter. Generate natural, engaging dialogue for video content. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )

        try:
            import json
            dialogue = json.loads(response.choices[0].message.content)
            return dialogue
        except Exception as e:
            print(f"Failed to parse dialogue JSON: {e}")
            raise Exception("Failed to generate dialogue")

    except Exception as e:
        print(f"Failed to generate dialogue: {e}")
        raise Exception("Failed to generate dialogue")

async def generate_camera_angles(input_data: VideoIdeaInput) -> List[Dict]:
    """Generate camera angles and movements using AI"""
    prompt = f"""Generate professional camera angles and movements for a {input_data.platform} video about: {input_data.idea}

    Video details:
    - Platform: {input_data.platform}
    - Duration: {input_data.duration}
    - Tone: {input_data.tone}
    - Target audience: {input_data.target_audience}

    Create 5-6 specific camera setups including:
    - Camera angle (eye level, high angle, low angle, over-shoulder, etc.)
    - Camera movement (static, pan, tilt, zoom, dolly, etc.)
    - Purpose/reason for this angle
    - When to use it in the video

    Format as JSON array with keys: angle, movement, purpose, timing
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional cinematographer. Generate specific camera angles and movements for video production. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        try:
            import json
            angles = json.loads(response.choices[0].message.content)
            return angles
        except Exception as e:
            print(f"Failed to parse camera angles JSON: {e}")
            raise Exception("Failed to generate camera angles")

    except Exception as e:
        print(f"Failed to generate camera angles: {e}")
        raise Exception("Failed to generate camera angles")

async def generate_music_suggestions(input_data: VideoIdeaInput) -> List[str]:
    """Generate music suggestions using AI"""
    prompt = f"""Generate specific music and audio suggestions for a {input_data.platform} video about: {input_data.idea}

    Video details:
    - Platform: {input_data.platform}
    - Duration: {input_data.duration}
    - Tone: {input_data.tone}
    - Target audience: {input_data.target_audience}

    Provide 5-7 specific music/audio suggestions including:
    - Type of music (genre, mood, energy level)
    - When to use it in the video (intro, background, outro, etc.)
    - Platform-specific considerations
    - Specific timing if relevant

    Consider trending audio for {input_data.platform} and match the {input_data.tone} tone.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a music supervisor for video content. Generate specific, actionable music suggestions for different platforms and content types."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )

        # Parse the response into a list
        music_text = response.choices[0].message.content
        suggestions = [line.strip() for line in music_text.split('\n') if line.strip() and not line.strip().startswith('#')]

        # Filter out empty lines and ensure we have at least some suggestions
        suggestions = [s for s in suggestions if len(s) > 10]

        if len(suggestions) < 3:
            raise Exception("Generated insufficient music suggestions")

        return suggestions[:7]  # Limit to 7 suggestions

    except Exception as e:
        print(f"Failed to generate music suggestions: {e}")
        raise Exception("Failed to generate music suggestions")

async def generate_thumbnail_concepts(input_data: VideoIdeaInput) -> List[str]:
    """Generate thumbnail concepts using AI"""
    prompt = f"""Generate creative thumbnail concepts for a {input_data.platform} video about: {input_data.idea}

    Video details:
    - Platform: {input_data.platform}
    - Tone: {input_data.tone}
    - Target audience: {input_data.target_audience}

    Create 5-6 specific thumbnail concepts that:
    - Are optimized for {input_data.platform}
    - Match the {input_data.tone} tone
    - Will attract the {input_data.target_audience} audience
    - Include specific visual elements, colors, text placement
    - Are designed for high click-through rates

    Focus on what actually works on {input_data.platform} for this type of content.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a thumbnail designer expert. Generate specific, actionable thumbnail concepts that drive clicks and engagement on different platforms."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )

        # Parse the response into a list
        thumbnail_text = response.choices[0].message.content
        concepts = [line.strip() for line in thumbnail_text.split('\n') if line.strip() and not line.strip().startswith('#')]

        # Filter and clean up concepts
        concepts = [c for c in concepts if len(c) > 15]

        if len(concepts) < 3:
            raise Exception("Generated insufficient thumbnail concepts")

        return concepts[:6]  # Limit to 6 concepts

    except Exception as e:
        print(f"Failed to generate thumbnail concepts: {e}")
        raise Exception("Failed to generate thumbnail concepts")

async def generate_posting_strategy(input_data: VideoIdeaInput) -> Dict:
    """Generate platform-specific posting strategy using AI"""
    prompt = f"""Generate a comprehensive posting strategy for a {input_data.platform} video about: {input_data.idea}

    Video details:
    - Platform: {input_data.platform}
    - Duration: {input_data.duration}
    - Tone: {input_data.tone}
    - Target audience: {input_data.target_audience}

    Provide specific strategy including:
    - Best posting times for {input_data.platform}
    - Relevant hashtags (5-10 specific ones for this content)
    - Optimized description/caption
    - Engagement tactics specific to {input_data.platform}

    Format as JSON with keys: best_time, hashtags, description, engagement_tactics
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a social media strategist expert in {input_data.platform}. Generate specific, actionable posting strategies. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        try:
            import json
            strategy = json.loads(response.choices[0].message.content)
            return strategy
        except Exception as e:
            print(f"Failed to parse posting strategy JSON: {e}")
            raise Exception("Failed to generate posting strategy")

    except Exception as e:
        print(f"Failed to generate posting strategy: {e}")
        raise Exception("Failed to generate posting strategy")

async def generate_engagement_estimates(input_data: VideoIdeaInput) -> Dict:
    """Generate realistic engagement estimates"""
    base_multipliers = {
        "youtube": {"views": 1.0, "likes": 0.05, "shares": 0.01, "comments": 0.02},
        "instagram": {"views": 0.8, "likes": 0.08, "shares": 0.02, "comments": 0.03},
        "tiktok": {"views": 1.5, "likes": 0.1, "shares": 0.03, "comments": 0.04}
    }

    multiplier = base_multipliers.get(input_data.platform, base_multipliers["youtube"])
    base_views = 25000  # Base estimate

    return {
        "views": f"{int(base_views * multiplier['views'] * 0.6)}-{int(base_views * multiplier['views'] * 1.5)}",
        "likes": f"{int(base_views * multiplier['likes'] * 0.6)}-{int(base_views * multiplier['likes'] * 1.5)}",
        "shares": f"{int(base_views * multiplier['shares'] * 0.6)}-{int(base_views * multiplier['shares'] * 1.5)}",
        "comments": f"{int(base_views * multiplier['comments'] * 0.6)}-{int(base_views * multiplier['comments'] * 1.5)}",
        "retention_rate": "65-80%" if input_data.platform == "youtube" else "70-85%"
    }



@app.get("/")
async def root():
    return {"message": "AI Video Production Assistant API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
