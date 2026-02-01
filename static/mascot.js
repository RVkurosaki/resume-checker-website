// Interactive Mascot Expression System
(function () {
    const mascot = document.querySelector('.mascot');
    const bubble = document.querySelector('.bubble-text');

    if (!mascot || !bubble) return;

    // Get base path for mascot images
    const basePath = mascot.src.substring(0, mascot.src.lastIndexOf('/') + 1);

    // Mascot expression images
    const expressions = {
        standing: basePath + 'fox_standing.png',
        happy: basePath + 'fox_happy.png',
        thinking: basePath + 'fox_thinking.png',
        sad: basePath + 'fox_sad.png'
    };

    // Current state
    let currentExpression = 'standing';
    let isLocked = false; // Lock expression for score-based reactions
    let hoverTimeout = null;

    // Default message
    const defaultMessage = 'Hi! Hover over different sections to see me react!';

    // Expression mappings for different element types
    const expressionMap = {
        // Happy expressions - for positive actions
        'button[type="submit"]': { expression: 'happy', message: 'Ready? Let\'s do this! 💪' },
        '.btn-primary': { expression: 'happy', message: 'Click here to start the magic! ✨' },
        '.btn-success': { expression: 'happy', message: 'Great choice! Let\'s go! 🎉' },
        '.score-card': { expression: 'happy', message: 'Let\'s see your amazing results! 📊' },
        '.strength-item': { expression: 'happy', message: 'Wow! This is one of your strengths! 💪' },
        '.skill-tag': { expression: 'happy', message: 'You have this skill! Awesome! 🌟' },

        // Thinking expressions - for input and decision areas
        'input[type="text"]': { expression: 'thinking', message: 'Hmm... what should we enter here? 🤔' },
        'input[type="email"]': { expression: 'thinking', message: 'Your email address goes here! 📧' },
        'input[type="file"]': { expression: 'thinking', message: 'Select your resume file here! 📄' },
        'select': { expression: 'thinking', message: 'Let me think... what role are you targeting? 🎯' },
        'textarea': { expression: 'thinking', message: 'Time to write something thoughtful! ✍️' },
        '.file-label': { expression: 'thinking', message: 'Pick a resume to analyze! 📂' },
        '.upload-card': { expression: 'thinking', message: 'Upload your resume and let\'s see! 🔍' },
        '.feedback-section': { expression: 'thinking', message: 'Let me think about these suggestions... 💭' },
        '.suggestion-item': { expression: 'thinking', message: 'This is worth considering! 💡' },

        // Standing/neutral - for navigation and general elements
        'a': { expression: 'standing', message: 'Want to go there? I\'ll come with you! 👋' },
        '.nav-link': { expression: 'standing', message: 'Let\'s navigate together! 🧭' },
        '.feature-item': { expression: 'standing', message: 'Check out this cool feature! ⭐' },
        '.auth-card': { expression: 'standing', message: 'Welcome! Let\'s get you started! 👋' },

        // Sad - for negative elements
        '.missing-skills': { expression: 'sad', message: 'These skills are missing... let\'s add them! 😢' },
        '.error': { expression: 'sad', message: 'Oh no! Something went wrong... 😔' },
        'input[type="password"]': { expression: 'thinking', message: 'Keep your secret safe! 🔐' },
    };

    // Change mascot expression with smooth transition
    function changeMascotExpression(expression, message) {
        if (isLocked) return;

        if (expression !== currentExpression) {
            // Add fade effect
            mascot.style.opacity = '0.5';

            setTimeout(() => {
                mascot.src = expressions[expression];
                currentExpression = expression;
                mascot.style.opacity = '1';
            }, 150);
        }

        if (message) {
            bubble.textContent = message;
        }
    }

    // Reset to default state
    function resetMascot() {
        if (isLocked) return;

        changeMascotExpression('standing', defaultMessage);
    }

    // Check scores and set appropriate expression
    function checkScores() {
        const atsScore = document.querySelector('.ats-score .score-value');
        const jobMatchScore = document.querySelector('.job-match-score .score-value');
        const grammarScore = document.querySelector('.grammar-score .score-value');

        let lowScore = false;
        let sadMessage = '';

        if (atsScore) {
            const score = parseInt(atsScore.textContent);
            if (score < 60) {
                lowScore = true;
                sadMessage = 'Oh no... your ATS score is low. Let\'s improve it! 😢';
            }
        }

        if (!lowScore && jobMatchScore) {
            const score = parseInt(jobMatchScore.textContent);
            if (score < 50) {
                lowScore = true;
                sadMessage = 'Hmm... you\'re missing many required skills... 😔';
            }
        }

        if (!lowScore && grammarScore) {
            const score = parseInt(grammarScore.textContent);
            if (score < 70) {
                lowScore = true;
                sadMessage = 'Let\'s fix these grammar issues together! 📝';
            }
        }

        // Check for missing skills
        const missingSkillsList = document.querySelector('.missing-skills');
        if (!lowScore && missingSkillsList && missingSkillsList.children.length > 5) {
            lowScore = true;
            sadMessage = 'You need to add these skills to match better... 🤔';
        }

        if (lowScore) {
            isLocked = true;
            changeMascotExpression('sad', sadMessage);
            bubble.style.color = '#dc2626';
            // Unlock after 5 seconds
            setTimeout(() => {
                isLocked = false;
                bubble.style.color = '';
            }, 5000);
        } else if (atsScore || jobMatchScore) {
            // Good scores!
            changeMascotExpression('happy', 'Great job! Your scores look amazing! 🎉');
            setTimeout(resetMascot, 3000);
        }
    }

    // Setup hover detection for all interactive elements
    function setupHoverDetection() {
        Object.keys(expressionMap).forEach(selector => {
            const elements = document.querySelectorAll(selector);

            elements.forEach((element) => {
                // Skip if already has listener to prevent duplicates
                if (element.hasAttribute('data-mascot-listener')) {
                    return;
                }

                // Mark element as having listener
                element.setAttribute('data-mascot-listener', 'true');

                // Add event listeners WITHOUT replacing the element
                element.addEventListener('mouseenter', function () {
                    clearTimeout(hoverTimeout);
                    const config = expressionMap[selector];
                    if (config) {
                        changeMascotExpression(config.expression, config.message);
                    }
                }, { passive: true });

                element.addEventListener('mouseleave', function () {
                    // Delay reset to avoid flickering when moving between elements
                    clearTimeout(hoverTimeout);
                    hoverTimeout = setTimeout(resetMascot, 300);
                }, { passive: true });
            });
        });
    }

    // Initialize mascot system
    function init() {
        mascot.style.transition = 'opacity 0.2s ease';
        bubble.textContent = defaultMessage;

        setTimeout(() => {
            checkScores();
            setupHoverDetection();
        }, 500);
    }

    // Run initialization
    init();

    // Re-setup hover detection for dynamically loaded content
    setInterval(setupHoverDetection, 3000);

})();
