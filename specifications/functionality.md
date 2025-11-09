# Functional Requirements

1. **Data persistence Strategy**:
    - Data persistence will be file-based. Prefferable formats are markedown for text files and JSON for metadata.
    - Data with relations (projects, sessions, messages) will be stored in structured directories with JSON metadata files to maintain relationships.
    - For not accounted requirements a lightweight database (e.g., SQLite) can be considered in future iterations.

2. **Multi-User Support**:
    - The application is designed for single-user use. Multi-user support is out of scope for the initial implementation.

3. **Authentication & Security**:
    - API keys for AI providers will be stored securely in environment variables.
    - No user authentication is required for single-user application.

4. **Error Handling & Monitoring**:
    - Basic error handling will be implemented in all services.
    - Errors will be logged to console for debugging purposes.

5. **Testing Strategy**:
    - Unit tests will be written for core services.
    - Integration tests will be implemented for API endpoints.
    - End-to-end tests will be considered for critical user flows.

6. **Import/Export Functionality**:
    - Users can export chat histories and project data as JSON or markdown files.
    - Import functionality will allow users to load previously exported data back into the application.

7. **Message templates/prompts**:
    - Users can create, save, and manage message templates for common queries.
    - Templates can be selected and inserted into the chat input area.

8. **Session sharing**:
    - The application is a single-user application; session sharing is out of scope for the initial implementation.    

The application must fulfill the following functional requirements:

1. **Workspace organization. Principles:**
    - There are main chat, projects, and project workspaces.
    - Main chat is the default view when the application first starts. It is tied to specific default project which exists from the beginning. The default project functionality is the same as for other projects.
    - Projects are user-created entities that group related chats and files together in the project workspace.    
    - Projects can be nested within other projects.
    - Each chat is in its own session within a project. The session is needed to maintain separate histories and contexts for different conversations because of specifics of AI context handling. (For future) Chat can use other chat sessions if user will specify it.

2. **Main screen**
    Status: Partially Implemented
    - Main screen consists of:
        - Header with 
            - Application title and user profile information.
            - Search bar for finding messages and files.
            - Option selector "AI Provider" for switching AI models/providers.
        - Status bar displaying current project and chat session information.        
        - Sidebar for project and chat session navigation.        
        - Chat Area:
            - Displays chat messages in a conversational format.
            - Shows messages from both user and AI with timestamps.
            - Message input field for user to type and send messages.        
        - Sidebar:
            - Displays tree of Projects and Chat Session lists inside the current project.
            - Allows switching between Projects, Chat Sessions inside the current project.
            - On project selection the Project workspace is loaded (specication in its own use case)
            - On chat session selection the chat history for that session is loaded into the chat area. The current chat in chat area is saved before switching.
    - At application launch on the main screen user sees the last chat session he was working on last time.  

3. **User Settings Page**
    Status: To be implemented
   - Users can access a settings page to configure preferences.
   - User can set API keys for different AI providers (e.g., OpenAI, Anthropic) used by the application.
   - API keys are securely stored in environment variables and not hardcoded.
   - API keys are stored in a `.env` file at the project root.
   - User can change the API keys at any time via the settings page with .env file updated accordingly.
   - User can set default projects directory.

4. **AI Model communication**
    Status: To be implemented
   - The application communicates with AI models via their respective APIs.
   - The application supports multiple AI providers (e.g., OpenAI, Anthropic).
   - System select AI provider from option "AI Provider" on the main screen.
   - The application sends user messages to the selected AI provider and receives responses.
   - Responses are displayed in the chat interface.
   - The application handles API errors gracefully and informs the user.

4. **Projects**
    Status: To be implemented
    - Project can contain other projects as sub-projects (nested structure).
    - Each project has its own workspace containing files and chat sessions.
    - Project files are common for all chat sessions within the project.
    - Project workspaces is stored in its own directory in the user profile root directory.        
    - User can manage projects via the "Projects" page accessible from the sidebar on the main screen.
    - The "Projects" page displays a content of the workspace:
        - Files in the project workspace.
        - Chat sessions list associated with the project.
        - Controls to create, delete, rename Projects.    
    - Users can create new projects, specifying a unique name.    - Users can delete projects, which removes all associated files and chat histories.
    - Project can contain multiple chat sessions, each with its own history.

3. **Chat Sessions**
    Status: Not implemented
    - Chat sessions has its own directory inside the project workspace.
    - Chat sessions store their message histories in separate files within their directories.
    - Chat session has its own files stored in its directory.
    - For chat context files from the project workspace and from the chat session directory are used.
    - Users can create, open, and manage multiple chat sessions within each project.
    - Each chat session has its own history and context.
    - Users can switch between chat sessions easily within the project using the sidebar on the main screen.
    - Chat sessions are stored in the project workspace directory.
    - User can manage chat sessions via the "Chat Session" page accessible from the sidebar on the main screen.
    - The "Chat Sessions" page displays:
        - History of messages in the current chat session.
        - Controls to create, delete, and rename chat session.

4. **Chat Interface Prototype**
    Status: Implemented   
   - The chat interface displays messages from both the user and the AI in a conversational format.
    - Users can input messages via a text input field.
    - There is a time stamp displayed for each message.

5. ** Chat Interface**
    Status: To be implemented
    - The message input field supports multi-line text.
    - User can add attachments (files/images) to messages selecting them in the chat interface.
    - The chat interface supports markdown formatting for messages (bold, italics, code blocks, lists).
    - The chat interface supports displaying images and file attachments inline within the conversation.

4. **Backend API Endpoints**
    Status: To be implemented


