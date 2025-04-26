// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
    loadProjects();
    loadChats();
    // Get DOM elements
    const chatInput = document.getElementById('chat-input-field');
    const chatMessages = document.getElementById('chat-messages');
    const attachButton = document.getElementById('attach-button');
    const micButton = document.getElementById('mic-button');
    const optionsDots = document.querySelector('.options-dots');

    // Initialize title with test data (will be replaced with dynamic data later)
    // REM: This is temporarily hard-coded for testing
    // When connecting to LLM, these values will be set dynamically
    currentProject = "Business Development";
    currentChatName = "Sales Pipeline Review";
    updateTitle();

    // Send message function
    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        appendMessage(message, 'user');
        if (!currentChatName) {
            setChatTitleFromMessage(message);
        }
        chatInput.value = '';

        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'ai-message typing';
        typingIndicator.textContent = 'Thinking...';
        chatMessages.appendChild(typingIndicator);

        scrollToBottom();

        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            typingIndicator.remove();
            appendMessage(data.response, 'ai');
        })
        .catch(error => {
            console.error('Error:', error);
            typingIndicator.remove();

            const errorMessage = document.createElement('div');
            errorMessage.className = 'ai-message error';
            errorMessage.textContent = 'Sorry, I encountered an error. Please try again.';
            chatMessages.appendChild(errorMessage);

            scrollToBottom();
        });
    }

    // Append a message to the chat
    function appendMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = sender === 'user' ? 'user-message' : 'ai-message';
        messageElement.textContent = text;
        chatMessages.appendChild(messageElement);

        setTimeout(() => {
            scrollToBottom();
        }, 50);
    }

    // Scroll chat to bottom
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Open rename dialog
    function openRenameDialog() {
        alert("🛠️ This will allow you to rename the chat and project.");
    }

    // Event Listeners

    // Send message on Enter key
    if (chatInput) {
        chatInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                sendMessage();
            }
        });
    }

    // Attach button functionality
    if (attachButton) {
        attachButton.addEventListener('click', () => {
            alert('File attachment coming soon!');
        });
    }

    // Mic button functionality
    if (micButton) {
        micButton.addEventListener('click', () => {
            alert('Voice input coming soon!');
        });
    }

    // Bottom action buttons
    const bottomButtons = document.querySelectorAll('.bottom-action-button');
    bottomButtons.forEach(button => {
        button.addEventListener('click', () => {
            alert(`${button.textContent} functionality coming soon!`);
        });
    });

    // Top-right 3-dot menu (rename chat/project)
    if (optionsDots) {
        optionsDots.addEventListener('click', () => {
            openRenameDialog();
        });
    }

    // Auto focus input field when page loads
    if (chatInput) {
        chatInput.focus();
    }
    
    // Initialize projects
    const addProjectBtn = document.getElementById('add-project-button');
    if (addProjectBtn) {
        addProjectBtn.addEventListener('click', createNewProject);
    }
    const addRecentChatBtn = document.getElementById('add-recent-chat-button');
    if (addRecentChatBtn) {
        addRecentChatBtn.addEventListener('click', createNewRecentChat);
    }
    
    // Removed older chat add button functionality
    
    // Render initial projects and chats
    renderProjects();
    renderRecentChats();
    renderOlderChats();
});

// Dynamic project + chat name
let currentProject = null;
let currentChatName = null;

// Default fallback: use first 4 words from user input
function setChatTitleFromMessage(message) {
    const firstFour = message.split(/\s+/).slice(0, 4).join("_");
    currentChatName = firstFour;
    updateTitle();
}

// Update title function to correctly handle Project \ Chat format
function updateTitle() {
    const projectSpan = document.getElementById("project-name");
    const separatorSpan = document.querySelector(".title-separator");
    const chatSpan = document.getElementById("chat-name");
    
    if (!projectSpan || !separatorSpan || !chatSpan) {
        console.error("Title elements not found");
        return;
    }
    
    if (currentProject) {
        projectSpan.textContent = currentProject;
        projectSpan.style.display = "inline-block";
        separatorSpan.style.display = "inline-block";
    } else {
        projectSpan.style.display = "none";
        separatorSpan.style.display = "none";
    }
    
    chatSpan.textContent = currentChatName || "";
}

// Sample project data with more chats to demonstrate scrolling
// let projects = [
//     {
//         id: 1,
//         name: 'Project 1',
//         chats: [
//             { id: 101, name: 'Chat_1_in_project_1' },
//             { id: 102, name: 'Chat_2_in_project_1' },
//             { id: 103, name: 'Chat_3_in_project_1' },
//             { id: 104, name: 'Chat_4_in_project_1' },
//             { id: 105, name: 'Chat with a very long name that should truncate' }
//         ]
//     },
//     {
//         id: 2,
//         name: 'Project 2',
//         chats: [
//             { id: 201, name: 'Chat_1_in_project_2' },
//             { id: 202, name: 'Quarterly Reports Analysis' },
//             { id: 203, name: 'Marketing Strategy 2025' }
//         ]
//     },
//     {
//         id: 3,
//         name: 'Project with a very long name that should be truncated',
//         chats: [
//             { id: 301, name: 'Chat_1_in_project_3' },
//             { id: 302, name: 'Chat_2_in_project_3' },
//             { id: 303, name: 'Financial Overview Q1' },
//             { id: 304, name: 'Team Meeting Notes' }
//         ]
//     },
//     {
//         id: 4,
//         name: 'Project 4',
//         chats: [
//             { id: 401, name: 'Chat_1_in_project_4' },
//             { id: 402, name: 'Product Launch Timeline' }
//         ]
//     },
//     {
//         id: 5,
//         name: 'Business Development',
//         chats: [
//             { id: 501, name: 'Client Meeting Prep' },
//             { id: 502, name: 'Sales Pipeline Review' }
//         ]
//     },
//     {
//         id: 6,
//         name: 'Research Initiative',
//         chats: [
//             { id: 601, name: 'Literature Review' },
//             { id: 602, name: 'Experiment Results' },
//             { id: 603, name: 'Data Analysis Session' }
//         ]
//     },
//     {
//         id: 7,
//         name: 'Strategic Planning',
//         chats: [
//             { id: 701, name: 'Five Year Goals' },
//             { id: 702, name: 'SWOT Analysis' }
//         ]
//     }
// ];

// Function to render projects list
function renderProjects() {
    const projectList = document.getElementById('project-list');
    if (!projectList) return;
    
    projectList.innerHTML = '';
    
    projects.forEach(project => {
        // Create project container
        const projectItem = document.createElement('li');
        projectItem.className = 'project-item';
        
        // Create project name element
        const projectName = document.createElement('div');
        projectName.className = 'project-name';
        projectName.textContent = project.name;
        projectName.title = project.name; // Show full name on hover
        projectName.setAttribute('data-project-id', project.id);
        projectName.addEventListener('click', () => toggleProjectChats(project.id));
        
        // Create project actions
        const projectActions = document.createElement('div');
        projectActions.className = 'project-actions';
        
        // Settings gear button
        const settingsBtn = document.createElement('button');
        settingsBtn.className = 'project-action-btn settings-btn';
        settingsBtn.setAttribute('data-project-id', project.id);
        settingsBtn.title = 'Project settings';
        settingsBtn.innerHTML = `<svg class="gear-icon" viewBox="0 0 24 24">
            <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
        </svg>`;
        settingsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            showProjectSettings(project.id);
        });
        
        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'project-action-btn delete-btn';
        deleteBtn.setAttribute('data-project-id', project.id);
        deleteBtn.title = 'Delete project';
        deleteBtn.innerHTML = `<img src="/static/images/trash.png" alt="Delete" class="icon-image small">`;
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteProject(project.id);
        });
        
        // Add buttons to actions
        projectActions.appendChild(settingsBtn);
        projectActions.appendChild(deleteBtn);
        
        // Add elements to project item
        projectItem.appendChild(projectName);
        projectItem.appendChild(projectActions);
        
        // Add project item to list
        projectList.appendChild(projectItem);
        
        // Add chats for this project
        const chatList = document.createElement('ul');
        chatList.className = 'chat-list';
        chatList.id = `chats-for-project-${project.id}`;
        
        // For demonstration, show chats for first and third projects by default
        chatList.style.display = (project.id === 1 || project.id === 3) ? 'block' : 'none';
        
        project.chats.forEach(chat => {
            const chatItem = document.createElement('li');
            chatItem.className = 'chat-item';
            
            const chatName = document.createElement('div');
            chatName.className = 'chat-name';
            chatName.textContent = chat.name;
            chatName.title = chat.name;
            chatName.setAttribute('data-chat-id', chat.id);
            chatName.addEventListener('click', () => loadChat(chat.id, project.id));
            
            chatItem.appendChild(chatName);
            chatList.appendChild(chatItem);
        });
        
        projectList.appendChild(chatList);
    });
}

// Toggle project chats visibility
function toggleProjectChats(projectId) {
    const chatList = document.getElementById(`chats-for-project-${projectId}`);
    if (chatList) {
        chatList.style.display = chatList.style.display === 'none' ? 'block' : 'none';
    }
}

// Show project settings modal
function showProjectSettings(projectId) {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;
    
    const newName = prompt(`Edit project name:`, project.name);
    if (newName && newName.trim() && newName !== project.name) {
        project.name = newName.trim();
        renderProjects();
        
        // Update title if this is the current project
        if (currentProject === project.name) {
            currentProject = newName.trim();
            updateTitle();
        }
    }
}

// Delete project
function deleteProject(projectId) {
    if (confirm(`Are you sure you want to delete this project and all its chats?`)) {
        projects = projects.filter(p => p.id !== projectId);
        renderProjects();
    }
}

// Load a specific chat
function loadChat(chatId, projectId) {
    const project = projects.find(p => p.id === projectId);
    const chat = project ? project.chats.find(c => c.id === chatId) : null;
    
    if (project && chat) {
        // Set current project and chat name for title display
        currentProject = project.name;
        currentChatName = chat.name;
        updateTitle();
        
        // In the future, implement actual chat loading
        console.log(`Loading chat: ${chat.name} from project: ${project.name}`);
    }
}

// Create new project
function createNewProject() {
    const projectName = prompt('Enter new project name:');
    if (projectName && projectName.trim()) {
        const newId = Math.max(...projects.map(p => p.id), 0) + 1;
        projects.push({
            id: newId,
            name: projectName.trim(),
            chats: []
        });
        renderProjects();
    }
}

// Sample data for recent chats
// let recentChats = [
//     { id: 901, name: 'Mock Chat 1' },
//     { id: 902, name: 'Mock Chat 2' },
//     { id: 903, name: 'Mock Chat 3' },
//     { id: 904, name: 'Mock Chat 4' },
//     { id: 905, name: 'Mock Chat 5' },
//     { id: 906, name: 'Mock Chat 6' },
//     { id: 907, name: 'Mock Chat 7' },
//     { id: 908, name: 'Mock Chat 8' },
//     { id: 909, name: 'Mock Chat 9' },
//     { id: 910, name: 'Mock Chat 10' },
//     { id: 911, name: 'Mock Chat 11' },
//     { id: 912, name: 'Mock Chat 12' }
// ];

// Sample data for older chats
//let olderChats = [
//    { id: 801, name: 'Older Chat 1' },
//    { id: 802, name: 'Older Chat 2' },
//    { id: 803, name: 'Older Chat 3' },
//    { id: 804, name: 'Older Chat 4' },
//     { id: 805, name: 'Older Chat 5' },
//     { id: 806, name: 'Older Chat 6' },
//     { id: 807, name: 'Older Chat 7' },
//     { id: 808, name: 'Older Chat 8' },
//     { id: 809, name: 'Older Chat 9' },
//     { id: 810, name: 'Older Chat 10' },
//     { id: 811, name: 'Older Chat 11' },
//     { id: 812, name: 'Older Chat 12' }
// ];

// Render function for recent chats
function renderRecentChats() {
    const recentList = document.getElementById('recent-chat-list');
    if (!recentList) return;
    recentList.innerHTML = '';

    recentChats.forEach(chat => {
        const chatItem = document.createElement('li');
        chatItem.className = 'chat-item';

        // Chat name
        const chatName = document.createElement('div');
        chatName.className = 'chat-name';
        chatName.textContent = chat.name;
        chatName.title = chat.name;
        chatName.setAttribute('data-chat-id', chat.id);
        chatName.addEventListener('click', () => {
            currentProject = null;
            currentChatName = chat.name;
            updateTitle();
        });

        // Chat actions container
        const chatActions = document.createElement('div');
        chatActions.className = 'chat-actions';
        
        // Settings gear button
        const settingsBtn = document.createElement('button');
        settingsBtn.className = 'chat-action-btn settings-btn';
        settingsBtn.setAttribute('data-chat-id', chat.id);
        settingsBtn.title = 'Edit chat name';
        settingsBtn.innerHTML = `<svg class="gear-icon" viewBox="0 0 24 24">
            <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
        </svg>`;
        settingsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            renameChatDialog(chat.id, 'recent');
        });

        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'chat-action-btn delete-btn';
        deleteBtn.setAttribute('data-chat-id', chat.id);
        deleteBtn.title = 'Delete chat';
        deleteBtn.innerHTML = `<img src="/static/images/trash.png" alt="Delete" class="icon-image small">`;
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (confirm('Delete this chat?')) {
                recentChats = recentChats.filter(c => c.id !== chat.id);
                renderRecentChats();
            }
        });

        // Add buttons to actions
        chatActions.appendChild(settingsBtn);
        chatActions.appendChild(deleteBtn);
        
        // Add elements to chat item
        chatItem.appendChild(chatName);
        chatItem.appendChild(chatActions);
        recentList.appendChild(chatItem);
    });
}

// Render function for older chats
function renderOlderChats() {
    const olderList = document.getElementById('older-chat-list');
    if (!olderList) return;
    olderList.innerHTML = '';

    olderChats.forEach(chat => {
        const chatItem = document.createElement('li');
        chatItem.className = 'chat-item';

        // Chat name
        const chatName = document.createElement('div');
        chatName.className = 'chat-name';
        chatName.textContent = chat.name;
        chatName.title = chat.name;
        chatName.setAttribute('data-chat-id', chat.id);
        chatName.addEventListener('click', () => {
            currentProject = null;
            currentChatName = chat.name;
            updateTitle();
        });

        // Chat actions container
        const chatActions = document.createElement('div');
        chatActions.className = 'chat-actions';
        
        // Settings gear button
        const settingsBtn = document.createElement('button');
        settingsBtn.className = 'chat-action-btn settings-btn';
        settingsBtn.setAttribute('data-chat-id', chat.id);
        settingsBtn.title = 'Edit chat name';
        settingsBtn.innerHTML = `<svg class="gear-icon" viewBox="0 0 24 24">
            <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
        </svg>`;
        settingsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            renameChatDialog(chat.id, 'older');
        });

        // Delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'chat-action-btn delete-btn';
        deleteBtn.setAttribute('data-chat-id', chat.id);
        deleteBtn.title = 'Delete chat';
        deleteBtn.innerHTML = `<img src="/static/images/trash.png" alt="Delete" class="icon-image small">`;
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (confirm('Delete this chat?')) {
                olderChats = olderChats.filter(c => c.id !== chat.id);
                renderOlderChats();
            }
        });

        // Add buttons to actions
        chatActions.appendChild(settingsBtn);
        chatActions.appendChild(deleteBtn);
        
        // Add elements to chat item
        chatItem.appendChild(chatName);
        chatItem.appendChild(chatActions);
        olderList.appendChild(chatItem);
    });
}

// Function to rename a chat (works for both recent and older chats)
function renameChatDialog(chatId, chatType) {
    let chatArray, renderFunction;
    
    if (chatType === 'recent') {
        chatArray = recentChats;
        renderFunction = renderRecentChats;
    } else {
        chatArray = olderChats;
        renderFunction = renderOlderChats;
    }
    
    const chat = chatArray.find(c => c.id === chatId);
    if (!chat) return;
    
    const newName = prompt(`Edit chat name:`, chat.name);
    if (newName && newName.trim() && newName !== chat.name) {
        chat.name = newName.trim();
        renderFunction();
        
        // Update title if this is the current chat
        if (currentChatName === chat.name) {
            currentChatName = newName.trim();
            updateTitle();
        }
    }
}

// Create new recent chat
function createNewRecentChat() {
    const chatName = prompt('Enter a name for your new chat:');
    if (chatName && chatName.trim()) {
        const newId = Math.max(0, ...recentChats.map(c => c.id)) + 1;
        
        // If we already have 12 chats, replace the oldest one
        if (recentChats.length >= 12) {
            // Find the chat with the lowest ID (oldest)
            const oldestChatIndex = recentChats.reduce((lowest, current, index, array) => 
                current.id < array[lowest].id ? index : lowest, 0);
            
            // Replace it with the new chat
            recentChats[oldestChatIndex] = { id: newId, name: chatName.trim() };
        } else {
            // Otherwise just add the new chat
            recentChats.push({ id: newId, name: chatName.trim() });
        }
        
        renderRecentChats();
    }
}

// Removed createNewOlderChat function since we no longer have the add button

// Add these functions to your app.js file, ideally near the bottom

// File Modal Functionality
const fileModal = document.getElementById('file-upload-modal');
const fileButton = document.getElementById('file-button');
const closeFileModal = document.querySelector('#file-upload-modal .close-button');
const cancelFileButton = document.querySelector('#file-upload-modal .cancel-button');
const fileUploadForm = document.getElementById('file-upload-form');
const projectSelect = document.getElementById('project-select');

// Show file modal when file button is clicked
if (fileButton) {
    fileButton.addEventListener('click', () => {
        // Populate project dropdown
        populateProjectDropdown();
        fileModal.style.display = 'block';
    });
}

// Close file modal when X is clicked
if (closeFileModal) {
    closeFileModal.addEventListener('click', () => {
        fileModal.style.display = 'none';
    });
}

// Close file modal when Cancel is clicked
if (cancelFileButton) {
    cancelFileButton.addEventListener('click', () => {
        fileModal.style.display = 'none';
    });
}

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    if (event.target === fileModal) {
        fileModal.style.display = 'none';
    }
});

// Populate project dropdown in file upload form
function populateProjectDropdown() {
    if (!projectSelect) return;
    
    // Clear existing options except the first one
    while (projectSelect.options.length > 1) {
        projectSelect.remove(1);
    }
    
    // Add all projects
    projects.forEach(project => {
        const option = document.createElement('option');
        option.value = project.name;
        option.textContent = project.name;
        projectSelect.appendChild(option);
    });
    
    // If there's a current project, select it
    if (currentProject) {
        for (let i = 0; i < projectSelect.options.length; i++) {
            if (projectSelect.options[i].value === currentProject) {
                projectSelect.selectedIndex = i;
                break;
            }
        }
    }
}

// Handle file upload form submission
if (fileUploadForm) {
    fileUploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const formData = new FormData(fileUploadForm);
        
        // Show upload indicator in chat
        const uploadIndicator = document.createElement('div');
        uploadIndicator.className = 'file-upload-indicator';
        uploadIndicator.textContent = 'Uploading file...';
        chatMessages.appendChild(uploadIndicator);
        scrollToBottom();
        
        fetch('/file/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Remove upload indicator
            uploadIndicator.remove();
            
            if (data.status === 'success') {
                // Show success message
                showToast(`File ${data.filename} uploaded successfully`);
                
                // Add file message to chat
                const fileMessage = document.createElement('div');
                fileMessage.className = 'ai-message';
                fileMessage.innerHTML = `
                    <div class="file-message">
                        <div class="file-icon">📄</div>
                        <div class="file-details">
                            <div class="file-name">${data.filename}</div>
                            <div class="file-meta">Added to memory</div>
                        </div>
                    </div>
                    <p>I've processed the file "${data.filename}" and added it to my memory. You can now ask me questions about its contents.</p>
                `;
                chatMessages.appendChild(fileMessage);
                scrollToBottom();
                
                // Reset form and close modal
                fileUploadForm.reset();
                fileModal.style.display = 'none';
            } else {
                // Show error message
                showToast(`Error: ${data.message}`, 'error');
            }
        })
        .catch(error => {
            // Remove upload indicator
            uploadIndicator.remove();
            
            console.error('Error:', error);
            showToast('Error uploading file', 'error');
        });
    });
}

// Toast notification system
function showToast(message, type = 'success') {
    // Create toast container if it doesn't exist
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = 'toast' + (type === 'error' ? ' toast-error' : '');
    toast.innerHTML = `
        <div class="toast-message">${message}</div>
        <div class="toast-close">&times;</div>
    `;
    
    // Add to container
    container.appendChild(toast);
    
    // Remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
    
    // Close button functionality
    const closeButton = toast.querySelector('.toast-close');
    closeButton.addEventListener('click', () => {
        toast.remove();
    });
}

// New chat button functionality
const newChatButton = document.getElementById('new-chat-button');
if (newChatButton) {
    newChatButton.addEventListener('click', () => {
        // Ask if user wants to create in a project
        const useProject = confirm('Create chat in a project?');
        let projectName = null;
        
        if (useProject) {
            // Show list of projects
            let projectOptions = '';
            projects.forEach(project => {
                projectOptions += `${project.id}: ${project.name}\n`;
            });
            
            const projectChoice = prompt(`Enter project number:\n${projectOptions}`);
            if (projectChoice !== null) {
                const project = projects.find(p => p.id.toString() === projectChoice.trim());
                if (project) {
                    projectName = project.name;
                }
            }
        }
        
        // Ask for chat name
        const chatName = prompt('Enter name for new chat:');
        if (chatName) {
            createNewChat(projectName, chatName);
        }
    });
}

// Update voice button functionality
const voiceButton = document.getElementById('voice-button');
if (voiceButton) {
    voiceButton.addEventListener('click', () => {
        alert('Voice transcription coming soon!');
    });
}

// Update docs button functionality
const docsButton = document.getElementById('docs-button');
if (docsButton) {
    docsButton.addEventListener('click', () => {
        window.location.href = '/docs'; // Redirect to docs page (to be implemented)
    });
}

// Update search button functionality
const searchButton = document.getElementById('search-button');
if (searchButton) {
    searchButton.addEventListener('click', () => {
        window.location.href = '/search'; // Redirect to search page (to be implemented)
    });
}

// Add this at the beginning of loadChatData function
function loadChatData() {
    // First, clear existing messages
    chatMessages.innerHTML = '';
    
    // Fetch chat history from backend
    const chatId = document.getElementById('chat-id-holder')?.dataset?.chatId;
    if (!chatId) return;
    
    // Get chat name from DOM
    const chatNameElement = document.getElementById('chat-name');
    if (chatNameElement) {
        currentChatName = chatNameElement.textContent;
    }
    
    // Get project from DOM
    const projectNameElement = document.getElementById('project-name');
    if (projectNameElement) {
        currentProject = projectNameElement.textContent;
        // If empty, set to null
        if (!currentProject.trim()) {
            currentProject = null;
        }
    }
    
    // Now fetch the actual chat data from a session-maintained endpoint
    fetch(`/chat_data`)
        .then(response => response.json())
        .then(data => {
            if (data.history && data.history.length > 0) {
                // Render chat messages
                data.history.forEach(msg => {
                    appendMessage(msg.content, msg.role === 'assistant' ? 'ai' : 'user');
                });
                scrollToBottom();
            }
        })
        .catch(error => console.error('Error loading chat data:', error));
}

// Load projects from server
function loadProjects() {
    fetch('/get_projects')
        .then(response => response.json())
        .then(projects => {
            const projectList = document.getElementById('project-list');
            projectList.innerHTML = ''; // Clear existing projects
            
            if (projects.length === 0) {
                // If no projects, show a message
                const emptyItem = document.createElement('li');
                emptyItem.className = 'sidebar-item empty-item';
                emptyItem.textContent = 'No projects yet';
                projectList.appendChild(emptyItem);
            } else {
                // Add each project to the list
                projects.forEach(project => {
                    const projectItem = document.createElement('li');
                    projectItem.className = 'sidebar-item project-item';
                    projectItem.textContent = project;
                    projectItem.addEventListener('click', () => selectProject(project));
                    projectList.appendChild(projectItem);
                });
            }
        })
        .catch(error => console.error('Error loading projects:', error));
}

// Load chats from server
function loadChats() {
    fetch('/get_chats')
        .then(response => response.json())
        .then(chats => {
            const recentChatList = document.getElementById('recent-chat-list');
            const olderChatList = document.getElementById('older-chat-list');
            
            recentChatList.innerHTML = ''; // Clear existing chats
            olderChatList.innerHTML = ''; // Clear existing chats
            
            if (chats.length === 0) {
                // If no chats, show a message
                const emptyRecent = document.createElement('li');
                emptyRecent.className = 'sidebar-item empty-item';
                emptyRecent.textContent = 'No recent chats';
                recentChatList.appendChild(emptyRecent);
                
                const emptyOlder = document.createElement('li');
                emptyOlder.className = 'sidebar-item empty-item';
                emptyOlder.textContent = 'No older chats';
                olderChatList.appendChild(emptyOlder);
            } else {
                // Sort chats by date
                const currentDate = new Date();
                const oneWeekAgo = new Date(currentDate.getTime() - 7 * 24 * 60 * 60 * 1000);
                
                chats.forEach(chat => {
                    const chatDate = new Date(chat.last_updated);
                    const chatItem = document.createElement('li');
                    chatItem.className = 'sidebar-item chat-item';
                    chatItem.textContent = chat.name || `Chat ${chat.id.substring(0, 8)}`;
                    chatItem.addEventListener('click', () => loadChat(chat.id));
                    
                    // Add to recent or older list based on date
                    if (chatDate >= oneWeekAgo) {
                        recentChatList.appendChild(chatItem);
                    } else {
                        olderChatList.appendChild(chatItem);
                    }
                });
            }
        })
        .catch(error => console.error('Error loading chats:', error));
}

// Function to load a specific chat
function loadChat(chatId) {
    window.location.href = `/load_chat/${chatId}`;
}

// Function to select a project
function selectProject(projectName) {
    fetch('/set_project', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ project: projectName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            document.getElementById('project-name').textContent = projectName;
            // Optional: Update UI to highlight selected project
        }
    })
    .catch(error => console.error('Error setting project:', error));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadProjects();
    loadChats();
    
    // Setup event listeners for other UI elements
    // ...
});

// Add to your app.js file
function createNewProject() {
    const projectName = prompt('Enter new project name:');
    
    if (projectName && projectName.trim() !== '') {
        fetch('/create_project', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: projectName.trim() })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadProjects(); // Reload the project list
            } else {
                alert(data.message || 'Failed to create project');
            }
        })
        .catch(error => console.error('Error creating project:', error));
    }
}

// Don't forget to add the event listener in your DOMContentLoaded function:
document.getElementById('add-project-button').addEventListener('click', createNewProject);