import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
from config import Config
from openai_service import OpenAIService
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI TUTOR",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1976D2;
        margin-bottom: 2rem;
    }
    .status-indicator {
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        margin: 1rem 0;
        text-align: center;
    }
    .status-active {
        background-color: #4CAF50;
        color: white;
    }
    .status-inactive {
        background-color: #757575;
        color: white;
    }
    .stTextArea textarea {
        font-size: 16px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'config' not in st.session_state:
    try:
        st.session_state.config = Config()
        st.session_state.config.validate()
    except ValueError as e:
        st.error(f"❌ Configuration Error: {str(e)}")
        st.info("Please check your .env file and ensure all required variables are set.")
        st.stop()

if 'openai_service' not in st.session_state:
    st.session_state.openai_service = OpenAIService(st.session_state.config)
    st.session_state.openai_service.add_system_message(st.session_state.config.system_prompt)
    
    if st.session_state.config.enable_search:
        if (st.session_state.config.cog_search_endpoint and 
            st.session_state.config.cog_search_key and 
            st.session_state.config.cog_search_index):
            st.session_state.openai_service.set_data_sources(
                st.session_state.config.cog_search_endpoint,
                st.session_state.config.cog_search_key,
                st.session_state.config.cog_search_index,
                st.session_state.config.system_prompt
            )

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'session_active' not in st.session_state:
    st.session_state.session_active = False

if 'current_response' not in st.session_state:
    st.session_state.current_response = ""

if 'message_counter' not in st.session_state:
    st.session_state.message_counter = 0

# Title
st.markdown('<h1 class="main-header">🎓 AI TUTOR</h1>', unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("🎮 Controls")
    
    if st.session_state.session_active:
        st.markdown('<div class="status-indicator status-active">🟢 Session Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-indicator status-inactive">⚫ Session Inactive</div>', unsafe_allow_html=True)
    
    st.divider()
    
    if not st.session_state.session_active:
        if st.button("🚀 Start Avatar Session", key="start_session", use_container_width=True):
            st.session_state.session_active = True
            st.rerun()
    else:
        if st.button("⏹️ Stop Avatar Session", key="stop_session", use_container_width=True):
            st.session_state.session_active = False
            st.session_state.current_response = ""
            st.rerun()
    
    if st.session_state.session_active:
        st.divider()
        
        if st.button("🗑️ Clear Chat History", key="clear_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.openai_service.clear_messages()
            st.session_state.openai_service.add_system_message(st.session_state.config.system_prompt)
            st.session_state.current_response = ""
            st.success("Chat history cleared!")
            time.sleep(1)
            st.rerun()
        
        st.divider()
        st.markdown("""
        **💡 How to use:**
        
        **Voice Input:**
        - Click 🎤 button in video
        - Speak your question
        - Wait for response
        
        **Text Input:**
        - Type in box below
        - Click Send
        - Watch avatar respond
        """)

with col2:
    st.subheader("💬 Avatar & Captions")
    
    if st.session_state.session_active:
        config = st.session_state.config
        
        # Prepare response for avatar
        response_to_speak = st.session_state.current_response if st.session_state.current_response else "null"
        message_id = st.session_state.message_counter
        
        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/microsoft-cognitiveservices-speech-sdk@latest/distrib/browser/microsoft.cognitiveservices.speech.sdk.bundle-min.js"></script>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    background-color: #000;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    overflow: hidden;
                }}
                #container {{
                    width: 100%;
                    height: 600px;
                    position: relative;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                }}
                #videoPlayer {{
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                    background-color: #000;
                    z-index: 1; /* FIX: ensure video is above overlays */
                }}
                #debugLog {{
                    position: absolute;
                    top: 60px;
                    left: 15px;
                    background: rgba(0,0,0,0.9);
                    color: #0f0;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 11px;
                    max-width: 400px;
                    max-height: 200px;
                    overflow-y: auto;
                    z-index: 101;
                    font-family: monospace;
                }}
                #statusOverlay {{
                    position: absolute;
                    top: 15px;
                    left: 15px;
                    background: rgba(0,0,0,0.85);
                    color: #fff;
                    padding: 12px 20px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 500;
                    z-index: 100;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                    border: 1px solid rgba(255,255,255,0.1);
                }}
                #captionBox {{
                    position: absolute;
                    bottom: 90px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 85%;
                    max-width: 700px;
                    background: rgba(0,0,0,0.92);
                    color: #fff;
                    padding: 25px 30px;
                    border-radius: 12px;
                    font-size: 20px;
                    line-height: 1.6;
                    text-align: center;
                    z-index: 100;
                    display: none;
                    min-height: 70px;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.6);
                    border: 2px solid rgba(76, 175, 80, 0.3);
                    animation: fadeIn 0.3s ease-in;
                }}
                @keyframes fadeIn {{
                    from {{ opacity: 0; transform: translateX(-50%) translateY(10px); }}
                    to {{ opacity: 1; transform: translateX(-50%) translateY(0); }}
                }}
                #captionBox.user {{
                    border-color: rgba(33, 150, 243, 0.5);
                    background: rgba(21, 101, 192, 0.85);
                }}
                #micButton {{
                    position: absolute;
                    bottom: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
                    color: white;
                    border: none;
                    padding: 16px 35px;
                    border-radius: 30px;
                    cursor: pointer;
                    font-size: 17px;
                    font-weight: bold;
                    z-index: 100;
                    box-shadow: 0 4px 15px rgba(25, 118, 210, 0.4);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    border: 2px solid rgba(255,255,255,0.2);
                }}
                #micButton:hover:not(:disabled) {{
                    background: linear-gradient(135deg, #1565C0 0%, #0d47a1 100%);
                    transform: translateX(-50%) scale(1.05);
                    box-shadow: 0 6px 20px rgba(25, 118, 210, 0.6);
                }}
                #micButton:disabled {{
                    background: linear-gradient(135deg, #666 0%, #555 100%);
                    cursor: not-allowed;
                    opacity: 0.6;
                }}
                #micButton.listening {{
                    background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
                    animation: pulse 1.5s infinite;
                }}
                @keyframes pulse {{
                    0%, 100% {{ box-shadow: 0 4px 15px rgba(244, 67, 54, 0.4); }}
                    50% {{ box-shadow: 0 4px 25px rgba(244, 67, 54, 0.8); }}
                }}
            </style>
        </head>
        <body>
            <div id="container">
                <video id="videoPlayer" autoplay playsinline></video>
                <div id="statusOverlay">⚙️ Initializing...</div>
                <div id="debugLog"></div>
                <div id="captionBox"></div>
                <button id="micButton" disabled>🎤 Click to Speak</button>
            </div>
            
            <script>
                const SpeechSDK = window.SpeechSDK;
                let avatarSynthesizer = null;
                let speechRecognizer = null;
                let peerConnection = null;
                let isListening = false;
                let isSpeaking = false;
                let isInitialized = false;
                
                const config = {{
                    speechKey: "{config.speech_key}",
                    speechRegion: "{config.speech_region}",
                    ttsVoice: "{config.tts_voice}",
                    avatarCharacter: "{config.avatar_character}",
                    avatarStyle: "{config.avatar_style}",
                    sttLocales: "{','.join(config.stt_locales)}".split(',')
                }};
                
                const responseToSpeak = {json.dumps(response_to_speak)};
                const messageId = {message_id};
                let lastMessageId = -1;
                
                // Debug logging
                function debugLog(message) {{
                    console.log(message);
                    const debugDiv = document.getElementById('debugLog');
                    const timestamp = new Date().toLocaleTimeString();
                    debugDiv.innerHTML = `[${{timestamp}}] ${{message}}<br>` + debugDiv.innerHTML;
                    if (debugDiv.children.length > 10) {{
                        debugDiv.removeChild(debugDiv.lastChild);
                    }}
                }}
                
                function updateStatus(message, emoji = '⚙️') {{
                    document.getElementById('statusOverlay').innerHTML = emoji + ' ' + message;
                    debugLog(`Status: ${{message}}`);
                }}
                
                function showCaption(text, isUser = false) {{
                    const captionBox = document.getElementById('captionBox');
                    captionBox.textContent = text;
                    captionBox.className = isUser ? 'user' : '';
                    captionBox.style.display = 'block';
                }}
                
                function hideCaption() {{
                    document.getElementById('captionBox').style.display = 'none';
                }}
                
                async function initializeAvatar() {{
                    try {{
                        debugLog('Starting avatar initialization...');
                        updateStatus('Connecting to Avatar...', '🔄');
                        
                        const tokenUrl = "{config.get_avatar_token_url()}";
                        debugLog(`Token URL: ${{tokenUrl}}`);
                        
                        const response = await fetch(tokenUrl, {{
                            headers: {{
                                'Ocp-Apim-Subscription-Key': config.speechKey
                            }}
                        }});
                        
                        debugLog(`Token response status: ${{response.status}}`);
                        
                        if (!response.ok) {{
                            throw new Error('Failed to get ICE token: ' + response.status);
                        }}
                        
                        const tokenData = await response.json();
                        debugLog('ICE token received');
                        
                        peerConnection = new RTCPeerConnection({{
                            iceServers: [{{
                                urls: tokenData.Urls,
                                username: tokenData.Username,
                                credential: tokenData.Password
                            }}]
                        }});
                        
                        debugLog('RTCPeerConnection created');
                        
                        peerConnection.ontrack = (event) => {{
                            debugLog(`Track received: ${{event.track.kind}}`);
                            const videoPlayer = document.getElementById('videoPlayer');
                            if (videoPlayer.srcObject !== event.streams[0]) {{
                                videoPlayer.srcObject = event.streams[0];
                                debugLog('Video stream connected to player');
                            }}
                        }};
                        
                        peerConnection.oniceconnectionstatechange = () => {{
                            debugLog(`ICE State: ${{peerConnection.iceConnectionState}}`);
                            if (peerConnection.iceConnectionState === 'connected') {{
                                updateStatus('Avatar Ready', '🟢');
                                document.getElementById('micButton').disabled = false;
                                isInitialized = true;
                            }} else if (peerConnection.iceConnectionState === 'failed') {{
                                updateStatus('Connection Failed', '❌');
                                debugLog('ICE connection failed!');
                            }} else if (peerConnection.iceConnectionState === 'disconnected') {{
                                updateStatus('Disconnected', '⚠️');
                            }}
                        }};
                        
                        const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(
                            config.speechKey, 
                            config.speechRegion
                        );
                        speechConfig.speechSynthesisVoiceName = config.ttsVoice;
                        debugLog('Speech config created');
                        
                        const avatarConfig = new SpeechSDK.AvatarConfig(
                            config.avatarCharacter, 
                            config.avatarStyle
                        );
                        debugLog(`Avatar config: ${{config.avatarCharacter}} - ${{config.avatarStyle}}`);
                        
                        const videoFormat = new SpeechSDK.AvatarVideoFormat();
                        videoFormat.bitrate = 2000000;
                        avatarConfig.videoFormat = videoFormat;
                        
                        avatarSynthesizer = new SpeechSDK.AvatarSynthesizer(
                            speechConfig, 
                            avatarConfig
                        );
                        
                        debugLog('Avatar synthesizer created');
                        
                        avatarSynthesizer.avatarEventReceived = (s, e) => {{
                            debugLog(`Avatar event: ${{e.description}}`);
                        }};
                        
                        peerConnection.addTransceiver('video', {{ direction: 'sendrecv' }});
                        peerConnection.addTransceiver('audio', {{ direction: 'sendrecv' }});
                        debugLog('Transceivers added');
                        
                        debugLog('Starting avatar...');
                        const result = await avatarSynthesizer.startAvatarAsync(peerConnection);
                        debugLog(`Avatar start result: ${{result.reason}}`);
                        
                        if (result.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {{
                            debugLog('✅ Avatar started successfully!');
                            initializeSpeechRecognizer();
                            
                            // Speak response if available
                            if (responseToSpeak && responseToSpeak !== 'null' && messageId > lastMessageId) {{
                                lastMessageId = messageId;
                                setTimeout(() => speak(responseToSpeak), 500);
                            }}
                        }} else {{
                            throw new Error('Failed to start avatar: ' + result.errorDetails);
                        }}
                        
                    }} catch (error) {{
                        debugLog(`❌ Error: ${{error.message}}`);
                        console.error('Error initializing avatar:', error);
                        updateStatus('Failed: ' + error.message, '❌');
                    }}
                }}
                
                function initializeSpeechRecognizer() {{
                    try {{
                        const speechConfig = SpeechSDK.SpeechConfig.fromSubscription(
                            config.speechKey, 
                            config.speechRegion
                        );
                        
                        const autoDetectConfig = SpeechSDK.AutoDetectSourceLanguageConfig.fromLanguages(
                            config.sttLocales
                        );
                        
                        const audioConfig = SpeechSDK.AudioConfig.fromDefaultMicrophoneInput();
                        
                        speechRecognizer = SpeechSDK.SpeechRecognizer.FromConfig(
                            speechConfig,
                            autoDetectConfig,
                            audioConfig
                        );
                        
                        speechRecognizer.recognizing = (s, e) => {{
                            if (e.result.text) {{
                                showCaption('🎤 ' + e.result.text, true);
                            }}
                        }};
                        
                        speechRecognizer.recognized = (s, e) => {{
                            if (e.result.reason === SpeechSDK.ResultReason.RecognizedSpeech) {{
                                const text = e.result.text;
                                if (text && text.trim()) {{
                                    debugLog(`✅ Recognized: ${{text}}`);
                                    showCaption('You said: ' + text, true);
                                    sendMessageToStreamlit(text);
                                    setTimeout(stopListening, 500);
                                }}
                            }} else if (e.result.reason === SpeechSDK.ResultReason.NoMatch) {{
                                debugLog('No speech recognized');
                                showCaption('No speech detected. Please try again.', true);
                                setTimeout(() => {{
                                    hideCaption();
                                    stopListening();
                                }}, 2000);
                            }}
                        }};
                        
                        speechRecognizer.canceled = (s, e) => {{
                            debugLog(`Recognition canceled: ${{e.reason}}`);
                            if (e.reason === SpeechSDK.CancellationReason.Error) {{
                                debugLog(`Recognition error: ${{e.errorDetails}}`);
                                updateStatus('Recognition Error', '❌');
                            }}
                            stopListening();
                        }};
                        
                        debugLog('Speech recognizer initialized');
                    }} catch (error) {{
                        debugLog(`❌ Recognizer error: ${{error.message}}`);
                        console.error('Error initializing speech recognizer:', error);
                        updateStatus('Mic Error: ' + error.message, '❌');
                    }}
                }}
                
                function toggleMicrophone() {{
                    if (!isInitialized) {{
                        showCaption('Please wait, avatar is still initializing...', true);
                        setTimeout(hideCaption, 2000);
                        return;
                    }}
                    
                    if (isListening) {{
                        stopListening();
                    }} else {{
                        startListening();
                    }}
                }}
                
                function startListening() {{
                    if (isSpeaking) {{
                        showCaption('⏳ Please wait for avatar to finish speaking...', true);
                        setTimeout(hideCaption, 2000);
                        return;
                    }}
                    
                    if (speechRecognizer && !isListening) {{
                        hideCaption();
                        speechRecognizer.startContinuousRecognitionAsync(
                            () => {{
                                isListening = true;
                                const button = document.getElementById('micButton');
                                button.textContent = '🔴 Listening... (Click to stop)';
                                button.classList.add('listening');
                                updateStatus('Listening for your voice...', '🎤');
                                showCaption('🎤 Listening... Speak now!', true);
                                debugLog('✅ Speech recognition started');
                            }},
                            (err) => {{
                                debugLog(`❌ Failed to start recognition: ${{err}}`);
                                updateStatus('Failed to start microphone', '❌');
                                showCaption('Error: Could not start microphone', true);
                                setTimeout(hideCaption, 3000);
                            }}
                        );
                    }}
                }}
                
                function stopListening() {{
                    if (speechRecognizer && isListening) {{
                        speechRecognizer.stopContinuousRecognitionAsync(
                            () => {{
                                isListening = false;
                                const button = document.getElementById('micButton');
                                button.textContent = '🎤 Click to Speak';
                                button.classList.remove('listening');
                                updateStatus('Avatar Ready', '🟢');
                                debugLog('✅ Speech recognition stopped');
                            }},
                            (err) => {{
                                debugLog(`Failed to stop recognition: ${{err}}`);
                                isListening = false;
                            }}
                        );
                    }}
                }}
                
                async function speak(text) {{
                    if (!avatarSynthesizer || !text || text === 'null') return;
                    
                    debugLog(`Speaking: ${{text.substring(0, 50)}}...`);
                    isSpeaking = true;
                    updateStatus('Speaking...', '💬');
                    showCaption(text, false);
                    
                    const ssml = `<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' 
                                   xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='en-US'>
                        <voice name='${{config.ttsVoice}}'>
                            <mstts:ttsembedding speakerProfileId=''>
                                <mstts:leadingsilence-exact value='0'/>
                            </mstts:ttsembedding>
                            ${{text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}}
                        </voice>
                    </speak>`;
                    
                    try {{
                        const result = await avatarSynthesizer.speakSsmlAsync(ssml);
                        
                        if (result.reason === SpeechSDK.ResultReason.SynthesizingAudioCompleted) {{
                            debugLog('✅ Speech synthesis completed');
                        }} else {{
                            debugLog(`❌ Speech synthesis failed: ${{result.errorDetails}}`);
                        }}
                        
                        setTimeout(() => {{
                            hideCaption();
                            isSpeaking = false;
                            updateStatus('Avatar Ready', '🟢');
                        }}, 1000);
                        
                    }} catch (error) {{
                        debugLog(`❌ Error speaking: ${{error.message}}`);
                        hideCaption();
                        isSpeaking = false;
                        updateStatus('Speech Error', '❌');
                    }}
                }}
                
                function sendMessageToStreamlit(text) {{
                    debugLog(`Sending to Streamlit: ${{text}}`);
                    window.parent.postMessage({{
                        type: 'voiceInput',
                        text: text,
                        timestamp: Date.now()
                    }}, '*');
                }}
                
                window.addEventListener('message', (event) => {{
                    if (event.data && event.data.type === 'speak' && event.data.text) {{
                        speak(event.data.text);
                    }}
                }});
                
                document.getElementById('micButton').addEventListener('click', toggleMicrophone);
                
                window.addEventListener('load', () => {{
                    debugLog('Page loaded, initializing avatar...');
                    setTimeout(initializeAvatar, 1200);
                }});
                
                if (responseToSpeak && responseToSpeak !== 'null') {{
                    debugLog(`Response ready: ${{responseToSpeak.substring(0, 50)}}...`);
                }}
            </script>
        </body>
        </html>
        """
        
        components.html(html_code, height=620)
    else:
        st.info("👆 Click 'Start Avatar Session' to begin")
    
    # Text input section
    if st.session_state.session_active:
        st.divider()
        st.markdown("### ⌨️ Type Your Message")
        
        col_input, col_send = st.columns([4, 1])
        
        with col_input:
            user_input = st.text_area(
                "Type your message here",
                key="user_text_input",
                height=100,
                placeholder="Type your question here and click Send...",
                label_visibility="collapsed"
            )
        
        with col_send:
            st.write("")
            st.write("")
            send_clicked = st.button("📤 Send", use_container_width=True, type="primary")
        
        if send_clicked and user_input and user_input.strip():
            with st.spinner("🤔 Thinking..."):
                try:
                    response = st.session_state.openai_service.get_chat_response(user_input)
                    
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': user_input,
                        'timestamp': datetime.now()
                    })
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response,
                        'timestamp': datetime.now()
                    })
                    
                    st.session_state.current_response = response
                    st.session_state.message_counter += 1
                    
                    st.success("✅ Message sent! Avatar will respond...")
                    time.sleep(0.5)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Error getting response: {e}")
    
    # Chat history
    if st.session_state.session_active:
        with st.expander("📜 View Chat History", expanded=False):
            if st.session_state.chat_history:
                for msg in reversed(st.session_state.chat_history[-10:]):
                    timestamp = msg.get('timestamp', datetime.now()).strftime("%H:%M:%S")
                    if msg['role'] == 'user':
                        st.markdown(f"**🗣️ You** `{timestamp}`")
                        st.info(msg['content'])
                    elif msg['role'] == 'assistant':
                        st.markdown(f"**🤖 Assistant** `{timestamp}`")
                        st.success(msg['content'])
                    st.divider()
            else:
                st.info("No conversation history yet. Start by typing or speaking!")

# Listen for voice input from iframe
components.html("""
<script>
    let lastReceivedText = null;
    
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'voiceInput' && event.data.text) {
            const text = event.data.text;
            
            if (text !== lastReceivedText) {
                lastReceivedText = text;
                console.log('Voice input received:', text);
                
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    key: 'voice_receiver',
                    value: {
                        text: text,
                        timestamp: Date.now()
                    }
                }, '*');
            }
        }
    });
</script>
""", height=0)

# Hidden component to receive voice input
voice_data = components.html("""
<div id="voice-receiver"></div>
<script>
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'voiceInput') {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: event.data
            }, '*');
        }
    });
</script>
""", height=0)

# Process voice input
if voice_data and isinstance(voice_data, dict) and 'text' in voice_data:
    voice_text = voice_data['text']
    
    if not hasattr(st.session_state, 'last_voice_text') or st.session_state.last_voice_text != voice_text:
        st.session_state.last_voice_text = voice_text
        
        with st.spinner("🤔 Processing your voice message..."):
            try:
                response = st.session_state.openai_service.get_chat_response(voice_text)
                
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': voice_text,
                    'timestamp': datetime.now()
                })
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now()
                })
                
                st.session_state.current_response = response
                st.session_state.message_counter += 1
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                logger.error(f"Error processing voice input: {e}")

# Footer
st.divider()
st.caption("🚀 AI Avatar Tutor | 🎤 Voice + ⌨️ Text Input | 💬 Real-time Captions")
