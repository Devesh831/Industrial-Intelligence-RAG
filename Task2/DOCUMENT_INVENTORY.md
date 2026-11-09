# Local document inventory

The genuine PDFs supplied for the assignment are present locally under `Task2/prototype/docs/` but are ignored by Git and are not copied into the public Render image. The public deployment indexes only two generated fictional PDFs.

| Document | Topic observed from extracted text |
|---|---|
| `172-65231ma.pdf` | TLV DC7 cyclone separator: safety, specifications, installation and troubleshooting |
| `43 86_Cyclone Separator_IandO.pdf` | Cyclone separator and sight-flow indicator installation and operating principle |
| `654b45bb8292f586313470.pdf` | Cyclone separator instructions for use, delivery, operation and maintenance |
| `B_12a.pdf` | Technical guidance on gas cyclones, particle separation and collection efficiency |
| `Cyclone_Emission_Control.pdf` | Woodmaster commercial cyclone separator owners manual, operation and safety |
| `Cyclone_Manual.pdf` | Kice cyclone collector operator manual, operation, maintenance and ATEX safety |
| `D13.pdf` | Cyclone dust collector design project and engineering principles |
| `Operating-and-maintenance-manual-for-a-typical-cylcone-seperator-.pdf` | Cyclonic dust separator installation, operation, explosion venting and maintenance |
| `Parker_DustHog_C_Series_Cyclone_Dust_Collector_User_Guide.pdf` | Parker DustHog C-Series cyclone dust collector operation and maintenance |
| `sect7a.pdf` | Cyclone classification, particle size separation and operating principles |
| `SOP Cyclone-22022023.pdf` | Government of India SOP for cyclones; meteorological/emergency procedure, not equipment maintenance |

Extraction emitted parser warnings for some malformed PDF objects, but text and page counts were readable. Questions must be evaluated against the actual corpus; the phrase “sudden draft drop” exists in the fictional demo guide, not in the supplied manuals, so a genuine-corpus run should abstain unless evidence is found.
