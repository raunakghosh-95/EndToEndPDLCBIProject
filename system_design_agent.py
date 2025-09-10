import os
import json
import re
from typing import Dict, List
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class SystemDesignAgent:
    """AI Agent that generates system design artifacts from BRD content with PLC-specific enhancements"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.temperature = 0.3
        
        # PLC-specific table mappings
        self.reporting_tables = {
            "dbo.[Rp_Alarms]": "Contains processed alarm, event, and message data for reports",
            "dbo.[Rp_BC_values]": "Summarized BC values data (float, string, tags) for reporting",
            "dbo.[Rp_Cure_DPP]": "Summarized Cure data (float, string, tags) for reporting based on DPP",
            "dbo.[Rp_Cure_EnvMon]": "Summarized Cure data (float, string, tags) for reporting based on Environment Monitoring",
            "dbo.[Rp_Cure_ExpTimes]": "Summarized Cure data (float, string, tags) for reporting based on Cureexposure times statistics",
            "dbo.[Rp_Cure_P1]": "Summarized Cure data (float, string, tags) for reporting based on Cure line part 1 processing",
            "dbo.[Rp_Cure_P2]": "Summarized Cure data (float, string, tags) for reporting based on Cure line part 2 processing",
            "dbo.[Rp_Cure_values]": "Aggregated Cure values from all stages (LH, LS, Tags)",
            "dbo.[Rp_Cure_Heaters]": "Heater performance metrics for Cure stage",
            "dbo.[Rp_Demold_performance]": "Demold process performance data",
            "dbo.[Rp_Demold_Metrics]": "Aggregated DemoldMetrics from all stages (LH, LS, Tags)",
            "dbo.[Rp_Demold_PID]": "PID control data for Demold stage",
            "dbo.[Rp_Demold_PID_Heaters]": "Heater data controlled by PID for Demold",
            "dbo.[Rp_EDHRD]": "Summarized EDHRD data (float, string, tags) for reporting",
            "dbo.[Rp_FC_Metrics]": "Aggregated FC Metrics from all stages (LH, LS, Tags)",
            "dbo.[Rp_GMS_Dev]": "GMS device-level performance data",
            "dbo.[Rp_GMS_M0]": "GMS module M0 operational metrics",
            "dbo.[Rp_GoodRejectPareto_Metrics]": "Aggregated GoodRejectPareto Metrics from all stages (LH, LS, Tags)",
            "dbo.[Rp_LED_devprophotonix]": "Summarized LED data (float, string, tags) for reporting",
            "dbo.[Rp_LensFab_Metrics]": "Aggregated LensFab Metrics from all stages (LH, LS, Tags)",
            "dbo.[Rp_Machine_OEE_Metrics]": "Aggregated OEE Metrics from all stages (LH, LS, Tags)",
            "dbo.[Rp_MachineConfig_BC]": "Configuration data specific to BC",
            "dbo.[Rp_MachineConfig_Cure]": "Configuration data specific to Cure",
            "dbo.[Rp_MachineConfig_Demold]": "Configuration data specific to Demold",
            "dbo.[Rp_MachineConfig_FC]": "Configuration data specific to FC",
            "dbo.[Rp_MachineConfig_FC_BC]": "Configuration data specific to FC_BC",
            "dbo.[Rp_MachineConfig_GMS]": "Configuration data specific to GMS",
            "dbo.[Rp_MachineConfig_Heated]": "Configuration data specific to Heated",
            "dbo.[Rp_MachineConfig_LensFab]": "Configuration data specific to Lensfab",
            "dbo.[Rp_MachineConfig_Precure]": "Configuration data specific to Precure",
            "dbo.[Rp_MachineConfig_Tween]": "Configuration data specific to Tween",
            "dbo.[Rp_MachineConfig_Vehicles]": "Configuration data specific to vehicles",
            "dbo.[Rp_O2_dev_Neutronics]": "O2 metrics from Neutronics devices",
            "dbo.[Rp_O2_M0]": "O2 module M0 data",
            "dbo.[Rp_PalletData_CavityPresence]": "Data related to cavity presence from pallet systems",
            "dbo.[Rp_PalletData_CavityStatus]": "Data related to cavity status from pallet systems",
            "dbo.[Rp_PalletData_ProcessCompletion]": "Data related to process completion from pallet systems",
            "dbo.[Rp_PalletData_ProcessExposures]": "Data related to Process Exposures from pallet systems",
            "dbo.[Rp_PalletData_ProcessTimeStamps]": "Data related to ProcessTimeStamps from pallet systems",
            "dbo.[Rp_PalletData_SKU]": "Data related to SKU from pallet systems",
            "dbo.[Rp_PalletData_Status]": "Data related to status from pallet systems",
            "dbo.[Rp_TrayData_CL]": "Summarized Tray data (float, string, tags) for reporting"
        }
        
        self.reporting_views = {
            "Vw_TB_AllEvent": "Allevents",
            "Vw_TB_Cure_devProPhotonix": "Cure",
            "Vw_TB_Cure_EnvMon": "Cure",
            "Vw_TB_Cure_LpDrv_Stats_ExpTimes": "Cure",
            "Vw_TB_Cure_M0_P1_Precure": "Cure",
            "Vw_TB_Cure_M0_P2_cure": "Cure",
            "Vw_TB_Cure_PID_Heaters": "Cure",
            "Vw_TB_Demold_M0_M1": "Demold",
            "Vw_TB_Demold_PID_Heaters": "Demold",
            "Vw_TB_Equipment_OEE": "OEE",
            "Vw_TB_GMS_dev": "GMS",
            "Vw_TB_GMS_M0": "GMS",
            "Vw_TB_GoodRejectPareto_Metrics": "Yield",
            "Vw_TB_LED_devprophotonix": "LED",
            "Vw_TB_LoopCount": "Yield",
            "Vw_TB_Machine_Metrics": "Downtime",
            "Vw_TB_MachineMetrics_PLC": "Downtime",
            "Vw_TB_O2_dev_Neutronics": "O2",
            "Vw_TB_O2_M0": "O2",
            "Vw_TB_OEE_Metrics": "OEE"
        }
        
        self.dashboards = ["Allevents", "Cure", "Demold", "OEE", "GMS", "Yield", "LED", "Downtime", "O2"]
        
    def _is_plc_content(self, brd_content: str) -> bool:
        """Check if content is PLC/manufacturing related"""
        plc_keywords = ['plc', 'sensor', 'cure', 'demold', 'oee', 'alarm', 'pallet', 'manufacturing', 'production', 'etl', 'power bi', 'dashboard']
        content_lower = brd_content.lower()
        return any(keyword in content_lower for keyword in plc_keywords)
        
    def analyze_brd(self, brd_content: str) -> Dict:
        """Phase 1: Analyze BRD and extract key entities with PLC-specific handling"""
        
        if self._is_plc_content(brd_content):
            system_prompt = f"""You are a highly experienced Senior Manufacturing Systems Architect and Solutions Designer specializing in PLC sensor data visualization systems.
Your task is to analyze the provided Business Requirements Document (BRD) content and extract all relevant information needed for creating a scalable, maintainable, and secure manufacturing data system design.

Specifically, identify and structure the following for PLC sensor data visualization:

1. **Manufacturing Entities:** PLC sensors, production stages (Cure, Demold, GMS, LED, O2), equipment, pallets, lots, processes, and their attributes/relationships.
2. **Data Processing Pipeline:** PLC sensors -> ODBC connection -> Staging tables -> ETL processes -> Reporting tables -> Views -> Power BI dashboards.
3. **Manufacturing Processes:** Production workflows, quality control, alarm management, OEE calculations, yield analysis.
4. **Performance Requirements:** Real-time constraints, dashboard refresh rates (5-15 minutes), alarm processing, data retention (2-year operational, 7-year batch records).
5. **Data Integration:** ETL views, stored procedures (Sp_Cure_DataLoad, Sp_Demold_DataLoad), incremental data loading.
6. **Manufacturing Data Flow:** Production tracking via LotID/PalletID/Timestamp, traceability requirements, quality metrics.
7. **System Architecture:** SQL Server database, Power BI Service, ODBC connections, Active Directory integration.

Known System Components:
- Reporting Tables: {len(self.reporting_tables)} tables including {', '.join(list(self.reporting_tables.keys())[:5])}...
- Views: {len(self.reporting_views)} optimized views for dashboards
- Dashboards: {', '.join(self.dashboards)}

Return the results as a **well-structured JSON object** with clear manufacturing-focused categories, subcategories, and details suitable for guiding PLC system architecture, UML diagrams, and manufacturing system design documents."""
        else:
            system_prompt = """You are a highly experienced Senior System Architect and Solutions Designer. 
Your task is to analyze the provided Business Requirements Document (BRD) content and extract all relevant information needed for creating a scalable, maintainable, and secure system design.

Specifically, identify and structure the following:

1. **Business Entities:** Key entities, their attributes, and relationships (e.g., User, Product, Order, Inventory).
2. **User Roles & Permissions:** All distinct user types and their access/authorization requirements.
3. **Functional Requirements:** Core use cases, workflows, and business processes.
4. **Non-Functional Requirements:** Performance, scalability, reliability, security, and compliance constraints.
5. **System Integrations:** External APIs, third-party services, databases, or messaging systems required.
6. **Data Flow & Dependencies:** Input/output data for each process, critical data paths, and storage requirements.
7. **Constraints & Assumptions:** Any dependencies, limitations, or conditions implied in the BRD.

Return the results as a **well-structured JSON object** with clear top-level categories, subcategories, and details suitable for guiding system architecture, UML diagrams, and design documents. Use descriptive keys and values, and avoid any irrelevant text."""
        
        user_prompt = f"""You are provided with the following BRD content. Carefully analyze it and generate a structured system analysis
in JSON format based on the system prompt instructions. Include all entities, roles, functional requirements, 
integrations, data flows, and constraints mentioned explicitly or implied.

BRD Content:
{brd_content}

Focus on actionable system design elements, ensuring that:
- Each entity includes attributes and relationships
- User roles specify permissions or actions
- Functional requirements are broken down by modules or features
- Data flow patterns and dependencies are clearly indicated
- Integrations and external system requirements are listed

Return only valid JSON without extra commentary or explanations."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            # Fallback if JSON parsing fails
            return {"analysis": response.choices[0].message.content}
    
    def generate_system_architecture(self, analysis: Dict) -> str:
        """Phase 2: Generate Mermaid system architecture diagram with PLC-specific handling"""
        
        if "manufacturing" in str(analysis).lower() or "plc" in str(analysis).lower() or "cure" in str(analysis).lower():
            system_prompt = f"""You are a manufacturing systems architect. Generate a Mermaid diagram showing the complete PLC sensor data visualization architecture:

REQUIRED COMPONENTS:
1. **Data Sources**: PLC Sensors (Cure, Demold, GMS, LED, O2)
2. **Data Pipeline**: ODBC Connection -> Staging Tables -> ETL Process -> Reporting Tables
3. **Data Layer**: {len(self.reporting_tables)} Reporting Tables -> {len(self.reporting_views)} Views
4. **Presentation**: Power BI Dashboards ({', '.join(self.dashboards)})
5. **Integration**: External systems (ERP, SCADA, Active Directory)
6. **Infrastructure**: SQL Server Database, Power BI Service

Show data flow direction and include key processes like incremental data loading, alarm processing, and real-time refresh.
Use Mermaid flowchart syntax with proper node connections."""
        else:
            system_prompt = """You are a system architect. Generate a Mermaid diagram showing:
            - High-level system components - Databases - External integrations 
            - User interfaces - API layers Keep it simple and focused.
            Use Mermaid flowchart syntax."""
        
        user_prompt = f"""Generate a Mermaid diagram based on the following system analysis JSON:
        
        {json.dumps(analysis, indent=2)}
        
Return **only the Mermaid diagram code**."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_use_case_diagram(self, analysis: Dict) -> str:
        """Phase 3: Generate PlantUML use case diagram with manufacturing-specific handling"""
        
        if "manufacturing" in str(analysis).lower() or "plc" in str(analysis).lower() or "cure" in str(analysis).lower():
            system_prompt = f"""Create a PlantUML use case diagram for a PLC sensor data visualization system with these actors and use cases:

ACTORS:
- Production Operator
- Process Engineer  
- Quality Manager
- Maintenance Technician
- Plant Manager
- System Administrator

MANUFACTURING USE CASES:
- Monitor Real-time Production
- View Equipment Status
- Analyze OEE Metrics
- Track Quality Trends
- Manage Alarms
- Generate Reports
- Configure Dashboards
- Maintain Data Pipeline

Focus on manufacturing operations and data visualization workflows. Use proper PlantUML syntax."""
        else:
            system_prompt = """You are a business analyst. Generate a PlantUML use case diagram showing:
            - Actors (users, systems)
            - Use cases (key functionalities)
            - Relationships between actors and use cases
            
            Keep it simple with 5-8 main use cases. Use proper PlantUML syntax."""
        
        user_prompt = f"""Based on this analysis, generate a PlantUML use case diagram:
        
        {json.dumps(analysis, indent=2)}
        
        Return ONLY PlantUML code starting with '@startuml' and ending with '@enduml'."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_sequence_diagram(self, analysis: Dict) -> str:
        """Phase 4: Generate PlantUML sequence diagram for main workflow with PLC-specific handling"""
        
        if "manufacturing" in str(analysis).lower() or "plc" in str(analysis).lower() or "cure" in str(analysis).lower():
            system_prompt = """Create a PlantUML sequence diagram showing the PLC data ingestion and visualization workflow:

PARTICIPANTS:
- PLC_Sensors
- ODBC_Connection  
- Staging_Tables
- ETL_Process
- Reporting_Tables
- Views_Layer
- PowerBI_Service
- Dashboard_User
- Alarm_System

MAIN SEQUENCE:
1. PLC sensors generate data
2. ODBC connection transfers data to staging
3. ETL process validates and transforms data
4. Data loaded into reporting tables
5. Views aggregate data for dashboards
6. Power BI refreshes and displays data
7. Users interact with dashboards
8. Alarms triggered for critical conditions

Show timing constraints (5-15 minute refresh cycles) and real-time alarm processing. Use proper PlantUML sequence syntax."""
        else:
            system_prompt = """You are a system designer. Generate a PlantUML sequence diagram showing:
            - Main user workflow/process
            - System components interaction
            - Key message flows
            
            Focus on one primary business process. Use proper PlantUML sequence syntax."""
        
        user_prompt = f"""Based on this analysis, generate a PlantUML sequence diagram:
        
        {json.dumps(analysis, indent=2)}
        
        Return ONLY PlantUML code starting with '@startuml' and ending with '@enduml'."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_class_diagram(self, analysis: Dict) -> str:
        """Phase 5: Generate PlantUML class diagram with manufacturing-specific handling"""
        
        if "manufacturing" in str(analysis).lower() or "plc" in str(analysis).lower() or "cure" in str(analysis).lower():
            system_prompt = f"""Create a PlantUML class diagram for the PLC sensor data model with these key classes:

CORE MANUFACTURING CLASSES:
- PLCSensor (SensorID, Type, Location, Status, LastReading)
- ProductionLot (LotID, StartTime, EndTime, Status, ProductType)
- Pallet (PalletID, LotID, CavityCount, Status, CurrentStage)
- ProcessStage (StageID, Name, Equipment, Parameters, Duration)
- AlarmEvent (AlarmID, Severity, Timestamp, Source, Category)
- OEEMetrics (Availability, Performance, Quality, OEEValue, Timestamp)
- QualityData (GoodCount, RejectCount, YieldPercent, DefectTypes)
- ReportingTable (TableName, LastUpdated, RecordCount)

RELATIONSHIPS:
- ProductionLot contains multiple Pallets (1:*)
- Pallet goes through ProcessStages (*:*)
- PLCSensor monitors ProcessStages (*:*)
- AlarmEvent generated by PLCSensor (*:1)
- OEEMetrics calculated from ProcessStage (1:*)
- QualityData linked to ProductionLot (1:1)

Include key attributes and show inheritance/composition relationships. Use proper PlantUML class syntax."""
        else:
            system_prompt = """You are a software architect. Generate a PlantUML class diagram showing:
            - Key business entities as classes
            - Attributes for each class (3-5 main ones)
            - Relationships between classes
            
            Keep it focused on core domain entities. Use proper PlantUML class syntax."""
        
        user_prompt = f"""Based on this analysis, generate a PlantUML class diagram:
        
        {json.dumps(analysis, indent=2)}
        
        Return ONLY PlantUML code starting with '@startuml' and ending with '@enduml'."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_er_diagram(self, analysis: Dict) -> str:
        """Phase 6: Generate Mermaid ER diagram with manufacturing-specific handling"""
        
        if "manufacturing" in str(analysis).lower() or "plc" in str(analysis).lower() or "cure" in str(analysis).lower():
            tables_list = list(self.reporting_tables.keys())[:12]  # Show first 12 tables for readability
            
            system_prompt = f"""Create a Mermaid ER diagram for the PLC sensor database with these key reporting tables:

CORE REPORTING TABLES:
{chr(10).join([f"- {table}" for table in tables_list])}

RELATIONSHIPS & KEYS:
- All tables link via common keys: LotID (string), PalletID (string), Timestamp (datetime)
- Rp_Alarms: AlarmID (PK), Severity, Source, Category, Timestamp, LotID
- Rp_Cure_values: CureID (PK), LotID, PalletID, Temperature, Pressure, Timestamp
- Rp_Demold_performance: DemoldID (PK), LotID, PalletID, CycleTime, Timestamp  
- Rp_Machine_OEE_Metrics: OEEID (PK), Equipment, Availability, Performance, Quality, Timestamp
- Rp_GoodRejectPareto_Metrics: QualityID (PK), LotID, GoodCount, RejectCount, Timestamp
- Rp_PalletData_ProcessCompletion: ProcessID (PK), PalletID, StageCompleted, Timestamp

Show primary keys (PK), foreign key relationships, and cardinality.
Focus on the most critical manufacturing tables for readability. Use Mermaid ER diagram syntax."""
        else:
            system_prompt = """You are a database architect. Generate a Mermaid ER diagram showing:
            - Key entities
            - Primary keys
            - Relationships with cardinality
            - Foreign key references
            
            Keep it simple with 5-8 main entities. Use Mermaid ER diagram syntax."""
        
        user_prompt = f"""Based on this analysis, generate a Mermaid ER diagram:
        
        {json.dumps(analysis, indent=2)}
        
        Return ONLY Mermaid code starting with 'erDiagram'."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_data_model_documentation(self, analysis: Dict) -> Dict:
        """Phase 7: Generate data model documentation with manufacturing-specific handling"""
        
        if "manufacturing" in str(analysis).lower() or "plc" in str(analysis).lower() or "cure" in str(analysis).lower():
            system_prompt = f"""Generate comprehensive data model documentation for the PLC sensor data visualization system:

INCLUDE:
1. **Manufacturing Data Architecture**: PLC sensors -> ODBC -> Staging -> Reporting -> Views -> Dashboards
2. **Table Schemas**: Field definitions, data types, constraints for key reporting tables
3. **Data Lineage**: Complete traceability from sensor readings to dashboard visualizations
4. **Key Relationships**: How LotID, PalletID, Timestamp provide production traceability
5. **Performance Optimization**: Indexing strategy for time-series manufacturing data
6. **Data Retention Policies**: 2-year operational data, 7-year batch records compliance
7. **ETL Processes**: Incremental loading via stored procedures (Sp_Cure_DataLoad, Sp_Demold_DataLoad)
8. **Dashboard Mappings**: Which views feed which manufacturing dashboards
9. **Manufacturing Metrics**: OEE calculations, yield analysis, alarm categorization
10. **Quality Assurance**: Data validation rules, error handling, audit trails

Known Components:
- Reporting Tables: {len(self.reporting_tables)} tables covering all production stages
- Views: {len(self.reporting_views)} optimized views for dashboard performance
- Dashboards: {', '.join(self.dashboards)} covering operational needs

Return structured JSON with manufacturing-focused documentation."""
        else:
            system_prompt = """You are a data architect. Generate comprehensive data model documentation with:
            1. Entity descriptions
            2. Table schemas (fields, types, constraints)
            3. Relationship explanations
            4. Index recommendations
            
            Return as structured JSON."""
        
        user_prompt = f"""Based on this analysis, generate data model documentation:
        
        {json.dumps(analysis, indent=2)}
        
        Return structured JSON with entities, schemas, and relationships."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {"documentation": response.choices[0].message.content}
    
    def generate_all_artifacts(self, brd_content: str) -> Dict:
        """Main method: Generate all system design artifacts with PLC-specific handling"""
        
        print("🔍 Phase 1: Analyzing BRD content...")
        analysis = self.analyze_brd(brd_content)
        
        print("🏗️ Phase 2: Generating system architecture...")
        system_arch = self.generate_system_architecture(analysis)
        
        print("👤 Phase 3: Generating use case diagram...")
        use_case = self.generate_use_case_diagram(analysis)
        
        print("⚡ Phase 4: Generating sequence diagram...")
        sequence = self.generate_sequence_diagram(analysis)
        
        print("📦 Phase 5: Generating class diagram...")
        class_diagram = self.generate_class_diagram(analysis)
        
        print("🗃️ Phase 6: Generating ER diagram...")
        er_diagram = self.generate_er_diagram(analysis)
        
        print("📚 Phase 7: Generating data model documentation...")
        data_docs = self.generate_data_model_documentation(analysis)
        
        # Enhanced metadata for PLC projects
        metadata = {
            "analysis": analysis,
            "system_architecture": system_arch,
            "use_case_diagram": use_case,
            "sequence_diagram": sequence,
            "class_diagram": class_diagram,
            "er_diagram": er_diagram,
            "data_model_docs": data_docs,
            "generated_at": datetime.now().isoformat()
        }
        
        # Add PLC-specific metadata if detected
        if self._is_plc_content(brd_content):
            metadata.update({
                "system_type": "PLC_Sensor_Data_Visualization",
                "reporting_tables_count": len(self.reporting_tables),
                "reporting_views_count": len(self.reporting_views),
                "dashboards": self.dashboards,
                "manufacturing_focus": True
            })
        
        return metadata
    
class DiagramRenderer:
    """Renders diagram code to viewable formats"""
    
    @staticmethod
    def clean_diagram_code(code: str, diagram_type: str) -> str:
        """Clean and validate diagram code"""
        code = code.strip()
        
        # Remove markdown code blocks if present
        code = re.sub(r'^```[\w]*\n', '', code)
        code = re.sub(r'\n```$', '', code)
        
        # Ensure proper start/end markers
        if diagram_type == "plantuml":
            if not code.startswith("@startuml"):
                code = "@startuml\n" + code
            if not code.endswith("@enduml"):
                code = code + "\n@enduml"
        elif diagram_type == "mermaid":
            if not code.startswith("graph ") and not code.startswith("erDiagram"):
                code = "graph TD\n" + code if "flowchart" in diagram_type else "erDiagram\n" + code
                
        return code
    
    @staticmethod
    def generate_html_preview(diagrams: Dict) -> str:
        """Generate HTML with embedded diagrams for preview"""
        
        # Prepare metadata section for PLC-specific projects
        metadata_section = ""
        if diagrams.get("manufacturing_focus", False):
            metadata_section += f"""
                <p><strong>System Type:</strong> {diagrams.get('system_type', 'N/A')}</p>
                <p><strong>Reporting Tables:</strong> {diagrams.get('reporting_tables_count', 0)}</p>
                <p><strong>Reporting Views:</strong> {diagrams.get('reporting_views_count', 0)}</p>
                <p><strong>Dashboards:</strong> {', '.join(diagrams.get('dashboards', []))}</p>
            """
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Design Diagrams</title>
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>mermaid.initialize({{startOnLoad:true}});</script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .diagram-section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .diagram-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
                .mermaid {{ text-align: center; background: #f9f9f9; padding: 10px; border-radius: 5px; }}
                .plantuml-code {{ 
                    background: #f5f5f5; 
                    padding: 10px; 
                    white-space: pre-wrap; 
                    font-family: monospace;
                    border-radius: 5px;
                }}
                .metadata {{ 
                    background: #e8f4fd; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>🏗️ System Design Diagrams</h1>
            <div class="metadata">
                <p><strong>Generated on:</strong> {diagrams.get('generated_at', 'N/A')}</p>
                {metadata_section}
            </div>
            
            <div class="diagram-section">
                <div class="diagram-title">📊 System Architecture</div>
                <div class="mermaid">{DiagramRenderer.clean_diagram_code(diagrams.get('system_architecture', ''), 'mermaid')}</div>
            </div>
            
            <div class="diagram-section">
                <div class="diagram-title">🗃️ Entity Relationship Diagram</div>
                <div class="mermaid">{DiagramRenderer.clean_diagram_code(diagrams.get('er_diagram', ''), 'mermaid')}</div>
            </div>
            
            <div class="diagram-section">
                <div class="diagram-title">👤 Use Case Diagram (PlantUML)</div>
                <div class="plantuml-code">{DiagramRenderer.clean_diagram_code(diagrams.get('use_case_diagram', ''), 'plantuml')}</div>
                <p><em>Copy this code to <a href="https://plantuml.com/plantuml" target="_blank">PlantUML Online</a> to render</em></p>
            </div>
            
            <div class="diagram-section">
                <div class="diagram-title">⚡ Sequence Diagram (PlantUML)</div>
                <div class="plantuml-code">{DiagramRenderer.clean_diagram_code(diagrams.get('sequence_diagram', ''), 'plantuml')}</div>
                <p><em>Copy this code to <a href="https://plantuml.com/plantuml" target="_blank">PlantUML Online</a> to render</em></p>
            </div>
            
            <div class="diagram-section">
                <div class="diagram-title">📦 Class Diagram (PlantUML)</div>
                <div class="plantuml-code">{DiagramRenderer.clean_diagram_code(diagrams.get('class_diagram', ''), 'plantuml')}</div>
                <p><em>Copy this code to <a href="https://plantuml.com/plantuml" target="_blank">PlantUML Online</a> to render</em></p>
            </div>
            
            <div class="diagram-section">
                <div class="diagram-title">📚 Data Model Documentation</div>
                <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">
                    {json.dumps(diagrams.get('data_model_docs', {}), indent=2)}
                </pre>
            </div>
        </body>
        </html>
        """
        return html_template
    
    @staticmethod
    def save_html_preview(html_content: str, output_path: str) -> None:
        """Save the HTML preview to a file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✅ HTML preview saved to {output_path}")
        except Exception as e:
            print(f"❌ Error saving HTML preview: {str(e)}")

# Example usage
if __name__ == "__main__":
    # Sample BRD content for testing
    sample_brd = """
    The system must collect real-time data from PLC sensors across Cure, Demold, and GMS stages. 
    Data is ingested via ODBC into staging tables, processed by ETL jobs (Sp_Cure_DataLoad, Sp_Demold_DataLoad), 
    and stored in reporting tables like Rp_Cure_values and Rp_Demold_performance. 
    Power BI dashboards (OEE, Yield, Allevents) refresh every 5-15 minutes. 
    System tracks LotID, PalletID, and Timestamp for traceability. 
    Alarms are processed in real-time and displayed on dashboards. 
    Data retention: 2 years operational, 7 years for batch records.
    """
    
    # Initialize agent and generate artifacts
    agent = SystemDesignAgent()
    artifacts = agent.generate_all_artifacts(sample_brd)
    
    # Render HTML preview
    renderer = DiagramRenderer()
    html_preview = renderer.generate_html_preview(artifacts)
    renderer.save_html_preview(html_preview, "system_design_preview.html")
