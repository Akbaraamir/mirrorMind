def get_pluto_logic(emotion):
    # This is your Action Space (A) structured as a dictionary for the UI
    flows = {
        "happy": {
            "emoji": "🌟", 
            "msg": "Mashallah! Your energy is like a bright star!", 
            "task": "Let's capture this 'Supernova' moment in your journal!"
        },
        "sad": {
            "emoji": "☁️", 
            "msg": "It looks like there are some clouds in your sky today, beta.", 
            "task": "Want to count 3 things that make you feel safe?"
        },
        "angry": {
            "emoji": "🔥", 
            "msg": "Whoa! It feels a bit like a volcano erupting!", 
            "task": "Let's do some 'Cool-Down' breathing together. Deep breath..."
        },
        "fear": {
            "emoji": "🛡️",
            "msg": "It's okay to feel a bit shaky in deep space.",
            "task": "Let's find 3 solid things around you to stay grounded."
        },
        "neutral": {
            "emoji": "🛰️", 
            "msg": "Everything is steady in orbit.", 
            "task": "What's one interesting thing you learned on your mission today?"
        },
    }
    
    # Default response if the emotion isn't in our list
    return flows.get(emotion, {
        "emoji": "🛸", 
        "msg": "I'm scanning your signal...", 
        "task": "How's your space mission going?"
    })