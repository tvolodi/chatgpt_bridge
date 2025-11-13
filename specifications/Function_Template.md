# Application Functionality Specification Template for Full Stack Development
Instructions: Use this template to document each functionality of the application, detailing the UI components involved and the backend API endpoints they interact with.
Use the text in angle brackets <> as placeholders to be filled in with specific information about the functionality being documented or as guidance for structuring the content.
---
## <Functionality Name>
    ### Status: <Not Started / In Progress / Implemented / Tested>
    ### Description (user story):
    <Detailed description of the function, its purpose, and how it fits into the overall system.>
    ### User interfaace (UI) components involved:
        #### Components <List of UI components that consist of or interact with this functionality.>:
        - <Component 1>:
            - Description: <Brief description of the component and its role in the functionality.>
            - <Identifiers / DOM Paths / Selectors>: <Relevant identifiers, DOM paths, or selectors used in the component (DOM paths refer to component position in the DOM tree, not file system paths).>            
            - Events: <List of events triggered by this component.> 
                - <Event 1>: <Description of the event and its purpose.>
                    - Backend API endpoints involved:
                    <GET /api/settings/api-providers/{provider_name}>
                - <Event 2>: <Description of the event and its purpose.>
                    - Backend API endpoints involved:
                    <PUT /api/settings/api-providers/{provider_name}>
        - <Component 2>...
    ### Backend API endpoints involved <list of services> <BACKEND_SWERVICES_PLAN.md used>:
        #### <service name>:
            Description: <Brief description of the service and its role in the functionality.>
            Status: <Not Started / In Progress / Implemented / Tested>
            URL: <POST /api/settings/api-providers/{provider_name}>            
##...