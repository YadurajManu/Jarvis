class JarvisUI {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.audioVisualizer = document.getElementById('audioVisualizer');
        this.voiceIndicator = document.querySelector('.voice-indicator');
        this.statusText = document.querySelector('.status-text');
        
        this.recognition = null;
        this.isListening = false;
        this.audioContext = null;
        this.analyser = null;
        this.visualizerStarted = false;
        
        this.initializeAudio();
        this.initializeSpeechRecognition();
        this.startupSequence();
    }
    
    startupSequence() {
        const bootMessages = [
            "Initializing systems...",
            "Calibrating sensors...",
            "Loading user preferences...",
            "Establishing neural interface...",
            "All systems operational."
        ];
        
        bootMessages.forEach((message, index) => {
            setTimeout(() => {
                this.addMessage(message, 'jarvis');
            }, index * 1000);
        });
        
        setTimeout(() => {
            this.addMessage("At your service, sir. How may I assist you today?", 'jarvis');
            this.startVoiceRecognition();
        }, bootMessages.length * 1000);
    }
    
    initializeAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            this.startVisualizer();
        } catch (e) {
            console.warn('Audio visualization not supported:', e);
        }
    }
    
    startVisualizer() {
        if (!this.audioContext || !this.analyser || this.visualizerStarted) return;
        
        const canvas = this.audioVisualizer;
        const ctx = canvas.getContext('2d');
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
        gradient.addColorStop(0, '#00A6FF');
        gradient.addColorStop(0.5, '#00FFA6');
        gradient.addColorStop(1, '#A6FF00');
        
        const draw = () => {
            const width = canvas.width = canvas.offsetWidth;
            const height = canvas.height = canvas.offsetHeight;
            
            this.analyser.getByteFrequencyData(dataArray);
            
            ctx.clearRect(0, 0, width, height);
            ctx.fillStyle = 'rgba(0, 166, 255, 0.1)';
            ctx.fillRect(0, 0, width, height);
            
            const barWidth = width / bufferLength * 2.5;
            let barHeight;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                barHeight = (dataArray[i] / 255) * height;
                
                ctx.fillStyle = gradient;
                ctx.fillRect(x, height - barHeight, barWidth, barHeight);
                
                x += barWidth + 1;
            }
            
            requestAnimationFrame(draw);
        };
        
        draw();
        this.visualizerStarted = true;
    }
    
    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new webkitSpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            
            this.recognition.onstart = () => {
                this.isListening = true;
                this.voiceIndicator.classList.add('active');
                this.statusText.textContent = "LISTENING...";
            };
            
            this.recognition.onresult = (event) => {
                const command = event.results[0][0].transcript;
                this.addMessage(command, 'user');
                this.processCommand(command);
            };
            
            this.recognition.onend = () => {
                this.isListening = false;
                this.voiceIndicator.classList.remove('active');
                this.statusText.textContent = "SYSTEM READY";
                setTimeout(() => this.startVoiceRecognition(), 1000);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.statusText.textContent = "ERROR DETECTED";
                setTimeout(() => {
                    this.statusText.textContent = "SYSTEM READY";
                    this.startVoiceRecognition();
                }, 2000);
            };
        } else {
            console.warn('Speech recognition not supported');
            this.addMessage("Speech recognition is not supported in this browser.", 'jarvis');
        }
    }
    
    startVoiceRecognition() {
        if (!this.recognition || this.isListening) return;
        try {
            this.recognition.start();
        } catch (e) {
            console.warn('Could not start recognition:', e);
        }
    }
    
    async processCommand(command) {
        try {
            const response = await this.sendCommand(command);
            this.addMessage(response, 'jarvis');
            this.triggerVisualizerEffect();
            this.speak(response);
        } catch (error) {
            console.error('Error processing command:', error);
            this.addMessage("I apologize, but I encountered an error processing your request.", 'jarvis');
        }
    }
    
    async sendCommand(command) {
        try {
            const response = await fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ command })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        messageDiv.textContent = text;
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    speak(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;
            
            const voices = speechSynthesis.getVoices();
            const preferredVoice = voices.find(voice => 
                voice.name.includes('Male') || 
                voice.name.includes('British') || 
                voice.name.includes('Daniel')
            );
            
            if (preferredVoice) {
                utterance.voice = preferredVoice;
            }
            
            speechSynthesis.speak(utterance);
        }
    }
    
    triggerVisualizerEffect() {
        if (!this.audioContext || !this.analyser) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.analyser);
        
        gainNode.gain.setValueAtTime(0.5, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5);
        
        oscillator.start();
        oscillator.stop(this.audioContext.currentTime + 0.5);
    }
}

// Initialize Jarvis UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
    window.jarvisUI = new JarvisUI();
});