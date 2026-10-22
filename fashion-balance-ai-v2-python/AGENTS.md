# Development requirements

- Backend language: Python / FastAPI. Frontend: React. Database: existing MySQL 8.
- Every feature must work on PC and phones. Mobile support is a default requirement, not an optional follow-up.
- Preserve the established editorial design, images, states, recommendation rules and detailed functionality.
- Inspect source and explain cause/plan before major changes. Never invent unseen code or external API specs.
- Keep sample/catalog data distinct from authenticated personal data. Check permissions on the server for every private resource.
- Never expose uploads as a public static directory or put credentials in the frontend.
- Test representative PC and mobile widths, touch controls, navigation, file selection, camera entry, loading/error states and saving.
- Report real-device/DB/email/API tests separately from browser emulation and mocks. Do not claim unperformed tests passed.
- After successful save, provide a clear route to the main screen and preserve an option to continue editing.
- Update README, schema/ERD, installation instructions and change history with relevant changes.

- Mobile home-screen installation must document HTTPS and online server requirements; never cache private API or photo responses in a service worker.
- Keep planning, functionality, screen design, DB dictionary, data sources, operations, deployment and acceptance documents aligned with implementation.
