import re
from typing import List, Dict, Tuple
import logging
import spacy
from sentence_transformers import SentenceTransformer, util
import numpy as np
from scipy.spatial.distance import cosine
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# Initialize NLP models (lazy loading for performance)
_nlp_model = None
_embedding_model = None
_spacy_model = None

def get_nlp_model():
    """Lazy load spaCy model"""
    global _spacy_model
    if _spacy_model is None:
        try:
            _spacy_model = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            _spacy_model = None
    return _spacy_model

def get_embedding_model():
    """Lazy load sentence transformer model"""
    global _embedding_model
    if _embedding_model is None:
        try:
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except:
            logger.warning("Sentence transformer model not found. Using fallback method.")
            _embedding_model = None
    return _embedding_model

# COMPREHENSIVE High-risk clinical keywords mapping - EXPANDED DATABASE
HIGH_RISK_KEYWORDS = {
    # ========== SYNTHETIC DISEASE KEYWORDS (Neuroflux Syndrome) ==========
    'brain fog': 'HIGH',
    'muscle heaviness': 'HIGH',
    'tremors': 'HIGH',
    'elevated nfm': 'HIGH',
    'neuroflux marker': 'HIGH',
    'delayed reflex': 'HIGH',
    'screen exposure': 'MODERATE',
    'irregular sleep': 'MODERATE',
    'caffeine intake': 'MODERATE',
    
    # ========== CRITICAL CONDITIONS (Life-threatening) ==========
    # Cardiac emergencies
    'chest pain': 'CRITICAL',
    'acute myocardial infarction': 'CRITICAL',
    'st elevation': 'CRITICAL',
    'myocardial infarction': 'CRITICAL',
    'cardiac tamponade': 'CRITICAL',
    'acute decompensated heart failure': 'CRITICAL',
    'cardiogenic shock': 'CRITICAL',
    'ventricular fibrillation': 'CRITICAL',
    'ventricular tachycardia': 'CRITICAL',
    'complete heart block': 'CRITICAL',
    'coronary artery dissection': 'CRITICAL',
    'acute aortic syndrome': 'CRITICAL',
    'aortic rupture': 'CRITICAL',
    'thunderclap headache': 'CRITICAL',
    'mi': 'CRITICAL',
    'heart attack': 'CRITICAL',
    'sudden cardiac death': 'CRITICAL',
    
    # Respiratory emergencies
    'shortness of breath': 'CRITICAL',
    'dyspnea': 'CRITICAL',
    'acute respiratory distress': 'CRITICAL',
    'respiratory failure': 'CRITICAL',
    'severe asthma': 'CRITICAL',
    'status asthmaticus': 'CRITICAL',
    'anaphylaxis': 'CRITICAL',
    'acute epiglottitis': 'CRITICAL',
    'tension pneumothorax': 'CRITICAL',
    'massive hemoptysis': 'CRITICAL',
    'laryngeal edema': 'CRITICAL',
    'stridor': 'CRITICAL',
    'severe hypoxia': 'CRITICAL',
    'hypoxemia': 'CRITICAL',
    'apnea': 'CRITICAL',
    'severe hypoxemia': 'CRITICAL',
    
    # Neurological emergencies
    'stroke': 'CRITICAL',
    'cerebral infarction': 'CRITICAL',
    'intracranial hemorrhage': 'CRITICAL',
    'subarachnoid hemorrhage': 'CRITICAL',
    'epidural hematoma': 'CRITICAL',
    'subdural hematoma': 'CRITICAL',
    'cerebral edema': 'CRITICAL',
    'status epilepticus': 'CRITICAL',
    'basilar artery occlusion': 'CRITICAL',
    'acute spinal cord compression': 'CRITICAL',
    'cauda equina syndrome': 'CRITICAL',
    'posterior reversible encephalopathy': 'CRITICAL',
    'meningitis': 'CRITICAL',
    'encephalitis': 'CRITICAL',
    'necrotizing fasciitis': 'CRITICAL',
    'intracerebral hemorrhage': 'CRITICAL',
    'subarachnoid bleed': 'CRITICAL',
    
    # Sepsis and infection
    'sepsis': 'CRITICAL',
    'septic shock': 'CRITICAL',
    'severe sepsis': 'CRITICAL',
    'toxic shock syndrome': 'CRITICAL',
    'severe infection': 'CRITICAL',
    'necrotizing infection': 'CRITICAL',
    'fournier gangrene': 'CRITICAL',
    'gas gangrene': 'CRITICAL',
    'fulminant infection': 'CRITICAL',
    
    # Metabolic emergencies
    'diabetic ketoacidosis': 'CRITICAL',
    'hyperosmolar hyperglycemic state': 'CRITICAL',
    'severe hyperglycemia': 'CRITICAL',
    'severe hypoglycemia': 'CRITICAL',
    'severe electrolyte abnormality': 'CRITICAL',
    'severe hyperkalemia': 'CRITICAL',
    'severe hypokalemia': 'CRITICAL',
    'severe hyponatremia': 'CRITICAL',
    'severe hypernatremia': 'CRITICAL',
    'severe acidosis': 'CRITICAL',
    'severe alkalosis': 'CRITICAL',
    'dka': 'CRITICAL',
    'hhs': 'CRITICAL',
    
    # Hemorrhage and coagulopathy
    'hemorrhage': 'CRITICAL',
    'massive bleeding': 'CRITICAL',
    'gastrointestinal hemorrhage': 'CRITICAL',
    'upper gi bleed': 'CRITICAL',
    'variceal bleeding': 'CRITICAL',
    'disseminated intravascular coagulation': 'CRITICAL',
    'severe thrombocytopenia': 'CRITICAL',
    'severe anemia': 'CRITICAL',
    'transfusion reaction': 'CRITICAL',
    'dic': 'CRITICAL',
    'active hemorrhage': 'CRITICAL',
    
    # Other critical conditions
    'unconscious': 'CRITICAL',
    'unresponsive': 'CRITICAL',
    'cardiac arrest': 'CRITICAL',
    'asystole': 'CRITICAL',
    'pulseless': 'CRITICAL',
    'shock': 'CRITICAL',
    'multiorgan failure': 'CRITICAL',
    'acute liver failure': 'CRITICAL',
    'acute kidney injury': 'CRITICAL',
    'acute respiratory distress syndrome': 'CRITICAL',
    'ards': 'CRITICAL',
    'acute pancreatitis': 'CRITICAL',
    'acute abdomen': 'CRITICAL',
    'bowel perforation': 'CRITICAL',
    'ruptured appendix': 'CRITICAL',
    'ruptured aorta': 'CRITICAL',
    'placental abruption': 'CRITICAL',
    'severe pre-eclampsia': 'CRITICAL',
    'eclampsia': 'CRITICAL',
    'amniotic fluid embolism': 'CRITICAL',
    'massive transfusion protocol': 'CRITICAL',
    'trauma with significant injury': 'CRITICAL',
    'airway emergency': 'CRITICAL',
    'airway compromise': 'CRITICAL',
    
    # ========== HIGH RISK CONDITIONS ==========
    # Pulmonary
    'pneumonia': 'HIGH',
    'aspiration pneumonia': 'HIGH',
    'community acquired pneumonia': 'HIGH',
    'hospital acquired pneumonia': 'HIGH',
    'ventilator associated pneumonia': 'HIGH',
    'pulmonary edema': 'HIGH',
    'acute decompensated heart failure': 'HIGH',
    'pulmonary hemorrhage': 'HIGH',
    'acute bronchitis': 'HIGH',
    'severe cough': 'HIGH',
    'pneumonitis': 'HIGH',
    'interstitial pneumonia': 'HIGH',
    'atypical pneumonia': 'HIGH',
    
    # Cardiovascular
    'arrhythmia': 'HIGH',
    'atrial fibrillation with rapid rate': 'HIGH',
    'bradycardia': 'HIGH',
    'tachycardia': 'HIGH',
    'hypertensive crisis': 'HIGH',
    'hypertensive urgency': 'HIGH',
    'acute coronary syndrome': 'HIGH',
    'unstable angina': 'HIGH',
    'nstemi': 'HIGH',
    'stemi': 'HIGH',
    'pulmonary embolism': 'HIGH',
    'pe': 'HIGH',
    'deep vein thrombosis': 'HIGH',
    'dvt': 'HIGH',
    'peripheral arterial occlusion': 'HIGH',
    'acute limb ischemia': 'HIGH',
    'myocarditis': 'HIGH',
    'pericarditis': 'HIGH',
    'acute valve dysfunction': 'HIGH',
    'endocarditis': 'HIGH',
    'severe hypotension': 'HIGH',
    'syncope': 'HIGH',
    'presyncope': 'HIGH',
    'acute heart failure': 'HIGH',
    'chf exacerbation': 'HIGH',
    'acute coronary event': 'HIGH',
    'aortic aneurysm': 'HIGH',
    'aortic dissection': 'HIGH',
    
    # Gastrointestinal
    'severe abdominal pain': 'HIGH',
    'acute abdomen': 'HIGH',
    'acute gastroenteritis': 'HIGH',
    'acute pancreatitis': 'HIGH',
    'cholecystitis': 'HIGH',
    'cholangitis': 'HIGH',
    'appendicitis': 'HIGH',
    'diverticulitis': 'HIGH',
    'inflammatory bowel disease flare': 'HIGH',
    'ulcerative colitis': 'HIGH',
    'crohns disease': 'HIGH',
    'bowel obstruction': 'HIGH',
    'paralytic ileus': 'HIGH',
    'toxic megacolon': 'HIGH',
    'volvulus': 'HIGH',
    'severe gastroesophageal reflux': 'HIGH',
    'barrett esophagus': 'HIGH',
    'esophageal varices': 'HIGH',
    'gastrointestinal hemorrhage': 'HIGH',
    'bleeding ulcer': 'HIGH',
    'mesenteric ischemia': 'HIGH',
    
    # Genitourinary
    'acute urinary retention': 'HIGH',
    'acute prostatitis': 'HIGH',
    'acute pyelonephritis': 'HIGH',
    'urosepsis': 'HIGH',
    'renal colic': 'HIGH',
    'severe hematuria': 'HIGH',
    'acute renal failure': 'HIGH',
    'acute glomerulonephritis': 'HIGH',
    'rhabdomyolysis': 'HIGH',
    'myoglobinuria': 'HIGH',
    'acute kidney injury': 'HIGH',
    'aki': 'HIGH',
    
    # Orthopedic/Trauma
    'severe trauma': 'HIGH',
    'head injury': 'HIGH',
    'severe head injury': 'HIGH',
    'fracture': 'HIGH',
    'compound fracture': 'HIGH',
    'spinal fracture': 'HIGH',
    'pelvic fracture': 'HIGH',
    'severe burns': 'HIGH',
    'compartment syndrome': 'HIGH',
    'crush injury': 'HIGH',
    'amputation': 'HIGH',
    'severe lacerations': 'HIGH',
    'open fracture': 'HIGH',
    'multiple trauma': 'HIGH',
    
    # Neurological
    'severe headache': 'HIGH',
    'sudden severe headache': 'HIGH',
    'migraine with aura': 'HIGH',
    'cluster headache': 'HIGH',
    'trigeminal neuralgia': 'HIGH',
    'transient ischemic attack': 'HIGH',
    'tia': 'HIGH',
    'vertebral artery dissection': 'HIGH',
    'carotid artery dissection': 'HIGH',
    'seizure': 'HIGH',
    'first time seizure': 'HIGH',
    'repeated seizure': 'HIGH',
    'febrile seizure': 'HIGH',
    'weakness': 'HIGH',
    'paralysis': 'HIGH',
    'hemiparesis': 'HIGH',
    'paraplegia': 'HIGH',
    'quadriplegia': 'HIGH',
    'facial droop': 'HIGH',
    'speech difficulty': 'HIGH',
    'aphasia': 'HIGH',
    'altered consciousness': 'HIGH',
    'confusion': 'HIGH',
    'delirium': 'HIGH',
    'disorientation': 'HIGH',
    'severe dementia': 'HIGH',
    'acute confusion': 'HIGH',
    'altered mental status': 'HIGH',
    
    # Infectious disease
    'severe influenza': 'HIGH',
    'covid19 pneumonia': 'HIGH',
    'covid pneumonia': 'HIGH',
    'severe covid19': 'HIGH',
    'coronavirus pneumonia': 'HIGH',
    'tuberculosis': 'HIGH',
    'disseminated tuberculosis': 'HIGH',
    'hiv aids': 'HIGH',
    'aids opportunistic infection': 'HIGH',
    'malaria': 'HIGH',
    'dengue fever': 'HIGH',
    'ebola': 'HIGH',
    'rabies': 'HIGH',
    'tetanus': 'HIGH',
    'measles': 'HIGH',
    'meningococcemia': 'HIGH',
    'severe infection': 'HIGH',
    'bloodstream infection': 'HIGH',
    'bacteremia': 'HIGH',
    
    # Endocrine
    'acute diabetes': 'HIGH',
    'thyroid storm': 'HIGH',
    'myxedema coma': 'HIGH',
    'adrenal crisis': 'HIGH',
    'severe hyperthyroidism': 'HIGH',
    'severe hypothyroidism': 'HIGH',
    'hyperthyroid crisis': 'HIGH',
    
    # Hematologic
    'acute leukemia': 'HIGH',
    'acute lymphoblastic leukemia': 'HIGH',
    'acute myeloid leukemia': 'HIGH',
    'tumor lysis syndrome': 'HIGH',
    'sickle cell crisis': 'HIGH',
    'thalassemia major': 'HIGH',
    'hemolytic anemia': 'HIGH',
    'severe anemia': 'HIGH',
    'hemophilia': 'HIGH',
    'von willebrand disease': 'HIGH',
    'bleeding disorder': 'HIGH',
    'coagulation disorder': 'HIGH',
    
    # Obstetric
    'severe pre-eclampsia': 'HIGH',
    'eclampsia': 'HIGH',
    'hellp syndrome': 'HIGH',
    'placental abruption': 'HIGH',
    'placenta previa': 'HIGH',
    'retained placenta': 'HIGH',
    'postpartum hemorrhage': 'HIGH',
    'amniotic fluid embolism': 'HIGH',
    'severe pregnancy complication': 'HIGH',
    'preeclampsia': 'HIGH',
    'labor complications': 'HIGH',
    
    # ========== MODERATE RISK CONDITIONS ==========
    'hypertension': 'MODERATE',
    'diabetes': 'MODERATE',
    'asthma': 'MODERATE',
    'copd': 'MODERATE',
    'chronic kidney disease': 'MODERATE',
    'heart disease': 'MODERATE',
    'atrial fibrillation': 'MODERATE',
    'cancer': 'MODERATE',
    'chemotherapy': 'MODERATE',
    'radiation therapy': 'MODERATE',
    'immunosuppressed': 'MODERATE',
    'hiv positive': 'MODERATE',
    'hepatitis': 'MODERATE',
    'cirrhosis': 'MODERATE',
    'liver disease': 'MODERATE',
    'obesity': 'MODERATE',
    'depression': 'MODERATE',
    'anxiety': 'MODERATE',
    'substance abuse': 'MODERATE',
    'alcoholism': 'MODERATE',
}

    @staticmethod
    def extract_chief_complaint(notes: str) -> str:
        """Extract chief complaint from clinical notes"""
        lines = notes.split('\n')
        for line in lines:
            if 'chief complaint' in line.lower() or 'cc:' in line.lower():
                return line.split(':', 1)[-1].strip()
        # Return first meaningful line if no explicit CC
        return next((line.strip() for line in lines if line.strip() and len(line.strip()) > 10), "Not specified")

    @staticmethod
    def extract_key_findings(notes: str) -> str:
        """Extract key findings from clinical notes - IMPROVED extraction"""
        findings = []
        notes_lower = notes.lower()
        
        # Keywords that indicate findings/symptoms/examination results
        finding_keywords = [
            'tremor', 'tremors', 'elevated', 'nfm', 'neuroflux marker',
            'reflex', 'examination shows', 'shows', 'present',
            'brain fog', 'muscle heaviness', 'weakness', 'fatigue',
            'pallor', 'cyanosis', 'edema', 'rash', 'fever',
            'heart rate', 'blood pressure', 'respiratory rate',
            'oxygen saturation', 'temperature', 'turgor',
            'decreased', 'increased', 'abnormal', 'delayed',
            'absent', 'present', 'positive', 'negative'
        ]
        
        # Extract sentences that contain critical findings
        sentences = notes.split('. ')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if sentence contains any finding indicator
            if any(keyword in sentence_lower for keyword in finding_keywords):
                # Skip sentences that are just history negations
                if not any(neg in sentence_lower for neg in ['no history', 'denies', 'negative for', 'ruled out', 'never']):
                    findings.append(sentence.strip())
        
        # Extract specific patterns like "X level is Y" or "X shows Y"
        if 'nfm' in notes_lower or 'neuroflux' in notes_lower:
            import re
            # Look for NFM levels
            nfm_match = re.search(r'nfm.*?(\d+\.?\d*)\s*units?', notes_lower)
            if nfm_match:
                findings.append(f"Serum Neuroflux Marker (NFM) elevated at {nfm_match.group(1)} units")
        
        # Clean up findings (remove duplicates and sort)
        findings = list(set(findings))[:5]
        
        return ' '.join(findings) if findings else "No specific findings documented"

    @staticmethod
    def detect_risk_words(notes: str) -> List[str]:
        """Detect risk words in clinical notes"""
        risk_words = []
        notes_lower = notes.lower()
        
        for keyword in HIGH_RISK_KEYWORDS.keys():
            if keyword in notes_lower:
                risk_words.append(keyword)
        
        return list(set(risk_words))

    @staticmethod
    def identify_risk_factors(notes: str, patient_age: str, gender: str) -> List[str]:
        """Identify clinical risk factors - EXPANDED DATABASE"""
        risk_factors = []
        notes_lower = notes.lower()
        
        # Age-based risk
        try:
            age = int(patient_age)
            if age > 75:
                risk_factors.append("Advanced age (>75)")
            elif age > 65:
                risk_factors.append("Advanced age (>65)")
            elif age < 5:
                risk_factors.append("Pediatric patient")
            elif age < 18:
                risk_factors.append("Adolescent patient")
        except:
            pass
        
        # Gender-specific risks
        if gender.lower() == 'female':
            if 'pregnant' in notes_lower or 'pregnancy' in notes_lower:
                risk_factors.append("Pregnant/Postpartum status")
            if 'postpartum' in notes_lower:
                risk_factors.append("Postpartum period")
        
        # ========== CARDIOVASCULAR CONDITIONS ==========
        cardiovascular_conditions = [
            ('hypertension', 'Hypertension'),
            ('heart disease', 'Cardiac disease'),
            ('coronary artery disease', 'Coronary artery disease'),
            ('acute coronary syndrome', 'Acute coronary syndrome'),
            ('congestive heart failure', 'Congestive heart failure'),
            ('chf', 'Heart failure'),
            ('ejection fraction', 'Ventricular dysfunction'),
            ('arrhythmia', 'Cardiac arrhythmia'),
            ('atrial fibrillation', 'Atrial fibrillation'),
            ('afib', 'Atrial fibrillation'),
            ('myocardial infarction', 'Prior myocardial infarction'),
            ('prior mi', 'Prior myocardial infarction'),
            ('previous stroke', 'Prior stroke'),
            ('transient ischemic attack', 'Transient ischemic attack'),
            ('tia', 'Transient ischemic attack'),
            ('valve disease', 'Valvular heart disease'),
            ('endocarditis', 'Endocarditis'),
            ('cardiomyopathy', 'Cardiomyopathy'),
            ('myocarditis', 'Myocarditis'),
            ('pericarditis', 'Pericarditis'),
            ('thrombophilia', 'Thrombophilia'),
            ('patent foramen ovale', 'Patent foramen ovale'),
            ('pfo', 'Patent foramen ovale'),
            ('aortic aneurysm', 'Aortic aneurysm'),
            ('aortic stenosis', 'Aortic stenosis'),
            ('mitral stenosis', 'Mitral stenosis'),
            ('hypertrophic cardiomyopathy', 'Hypertrophic cardiomyopathy'),
            ('dilated cardiomyopathy', 'Dilated cardiomyopathy'),
            ('marfan syndrome', 'Connective tissue disorder'),
            ('ehlers danlos', 'Connective tissue disorder'),
        ]
        
        for condition, label in cardiovascular_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== RESPIRATORY CONDITIONS ==========
        respiratory_conditions = [
            ('asthma', 'Asthma'),
            ('copd', 'Chronic obstructive pulmonary disease'),
            ('chronic obstructive pulmonary disease', 'COPD'),
            ('emphysema', 'Emphysema'),
            ('chronic bronchitis', 'Chronic bronchitis'),
            ('cystic fibrosis', 'Cystic fibrosis'),
            ('interstitial lung disease', 'Interstitial lung disease'),
            ('ild', 'Interstitial lung disease'),
            ('pulmonary fibrosis', 'Pulmonary fibrosis'),
            ('idiopathic pulmonary fibrosis', 'IPF'),
            ('ipf', 'Idiopathic pulmonary fibrosis'),
            ('pulmonary hypertension', 'Pulmonary hypertension'),
            ('obstructive sleep apnea', 'Sleep apnea'),
            ('osa', 'Obstructive sleep apnea'),
            ('sleep apnea', 'Sleep apnea'),
            ('lung cancer', 'Lung malignancy'),
            ('tuberculosis', 'Tuberculosis'),
            ('tb', 'Tuberculosis'),
            ('bronchiectasis', 'Bronchiectasis'),
            ('alpha-1 antitrypsin', 'Alpha-1 antitrypsin deficiency'),
        ]
        
        for condition, label in respiratory_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== ENDOCRINE CONDITIONS ==========
        endocrine_conditions = [
            ('diabetes', 'Diabetes mellitus'),
            ('type 1 diabetes', 'Type 1 diabetes'),
            ('type 2 diabetes', 'Type 2 diabetes'),
            ('insulin dependent', 'Insulin-dependent'),
            ('type 1 dm', 'Type 1 diabetes'),
            ('type 2 dm', 'Type 2 diabetes'),
            ('diabetic neuropathy', 'Diabetic complications'),
            ('diabetic retinopathy', 'Diabetic complications'),
            ('diabetic nephropathy', 'Diabetic complications'),
            ('thyroid disease', 'Thyroid disease'),
            ('hypothyroidism', 'Hypothyroidism'),
            ('hyperthyroidism', 'Hyperthyroidism'),
            ('graves disease', 'Graves disease'),
            ('thyroiditis', 'Thyroiditis'),
            ('hashimoto', 'Hashimoto thyroiditis'),
            ('adrenal insufficiency', 'Adrenal insufficiency'),
            ('cushings syndrome', 'Cushings syndrome'),
            ('pcos', 'Polycystic ovary syndrome'),
            ('menopause', 'Menopausal status'),
            ('hypogonadism', 'Hypogonadism'),
        ]
        
        for condition, label in endocrine_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== RENAL/URINARY CONDITIONS ==========
        renal_conditions = [
            ('chronic kidney disease', 'Chronic kidney disease'),
            ('ckd', 'Chronic kidney disease'),
            ('end stage renal disease', 'End stage renal disease'),
            ('esrd', 'End stage renal disease'),
            ('renal failure', 'Renal failure'),
            ('kidney transplant', 'Kidney transplant recipient'),
            ('dialysis', 'On dialysis'),
            ('proteinuria', 'Proteinuria'),
            ('hematuria', 'Hematuria'),
            ('polycystic kidney', 'Polycystic kidney disease'),
            ('glomerulonephritis', 'Glomerulonephritis'),
            ('nephrotic syndrome', 'Nephrotic syndrome'),
            ('nephritic syndrome', 'Nephritic syndrome'),
        ]
        
        for condition, label in renal_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== HEPATIC CONDITIONS ==========
        hepatic_conditions = [
            ('liver disease', 'Hepatic disease'),
            ('cirrhosis', 'Hepatic cirrhosis'),
            ('hepatitis', 'Hepatitis'),
            ('hepatitis a', 'Hepatitis A'),
            ('hepatitis b', 'Hepatitis B'),
            ('hepatitis c', 'Hepatitis C'),
            ('fatty liver', 'Fatty liver disease'),
            ('nafld', 'Non-alcoholic fatty liver disease'),
            ('portal hypertension', 'Portal hypertension'),
            ('varices', 'Esophageal varices'),
            ('liver transplant', 'Liver transplant recipient'),
            ('encephalopathy', 'Hepatic encephalopathy'),
        ]
        
        for condition, label in hepatic_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== NEUROLOGICAL CONDITIONS ==========
        neurological_conditions = [
            ('parkinson', 'Parkinsons disease'),
            ('alzheimer', 'Alzheimers disease'),
            ('dementia', 'Dementia'),
            ('multiple sclerosis', 'Multiple sclerosis'),
            ('ms', 'Multiple sclerosis'),
            ('epilepsy', 'Epilepsy'),
            ('seizure disorder', 'Seizure disorder'),
            ('migraine', 'Migraine disorder'),
            ('neuropathy', 'Neuropathy'),
            ('polyneuropathy', 'Polyneuropathy'),
            ('guillain barre', 'Guillain-Barre syndrome'),
            ('amyotrophic lateral sclerosis', 'Amyotrophic lateral sclerosis'),
            ('als', 'Amyotrophic lateral sclerosis'),
            ('motor neuron disease', 'Motor neuron disease'),
            ('myasthenia gravis', 'Myasthenia gravis'),
            ('muscular dystrophy', 'Muscular dystrophy'),
            ('cerebral palsy', 'Cerebral palsy'),
            ('spina bifida', 'Spina bifida'),
        ]
        
        for condition, label in neurological_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== GASTROINTESTINAL CONDITIONS ==========
        gi_conditions = [
            ('inflammatory bowel disease', 'Inflammatory bowel disease'),
            ('ibd', 'Inflammatory bowel disease'),
            ('ulcerative colitis', 'Ulcerative colitis'),
            ('crohns disease', 'Crohns disease'),
            ('gastroesophageal reflux', 'GERD'),
            ('gerd', 'GERD'),
            ('peptic ulcer', 'Peptic ulcer disease'),
            ('barrett esophagus', 'Barretts esophagus'),
            ('celiac disease', 'Celiac disease'),
            ('irritable bowel syndrome', 'Irritable bowel syndrome'),
            ('ibs', 'Irritable bowel syndrome'),
        ]
        
        for condition, label in gi_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== HEMATOLOGIC CONDITIONS ==========
        hematologic_conditions = [
            ('anemia', 'Anemia'),
            ('sickle cell', 'Sickle cell disease'),
            ('thalassemia', 'Thalassemia'),
            ('hemophilia', 'Hemophilia'),
            ('von willebrand', 'Von Willebrand disease'),
            ('leukemia', 'Leukemia'),
            ('lymphoma', 'Lymphoma'),
            ('multiple myeloma', 'Multiple myeloma'),
            ('thrombocytopenia', 'Thrombocytopenia'),
            ('idiopathic thrombocytopenia', 'ITP'),
            ('itp', 'Idiopathic thrombocytopenia'),
        ]
        
        for condition, label in hematologic_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== INFECTIOUS DISEASE ==========
        infectious_conditions = [
            ('hiv', 'HIV/AIDS'),
            ('aids', 'HIV/AIDS'),
            ('cd4 count', 'Immunocompromised'),
            ('immunocompromised', 'Immunocompromised status'),
            ('acquired immunodeficiency', 'AIDS'),
            ('hepatitis', 'Chronic viral hepatitis'),
            ('tuberculosis exposure', 'TB exposure'),
        ]
        
        for condition, label in infectious_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== MALIGNANCY & CANCER ==========
        cancer_conditions = [
            ('cancer', 'Active malignancy'),
            ('malignancy', 'Active malignancy'),
            ('tumor', 'Tumor'),
            ('chemotherapy', 'Undergoing chemotherapy'),
            ('radiation', 'Undergoing radiation therapy'),
            ('oncology', 'Oncology patient'),
            ('metastatic', 'Metastatic disease'),
            ('lymphoma', 'Lymphoma'),
            ('leukemia', 'Leukemia'),
            ('carcinoma', 'Carcinoma'),
            ('melanoma', 'Melanoma'),
        ]
        
        for condition, label in cancer_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== PSYCHIATRIC CONDITIONS ==========
        psychiatric_conditions = [
            ('depression', 'Major depression'),
            ('major depressive disorder', 'Major depression'),
            ('bipolar disorder', 'Bipolar disorder'),
            ('schizophrenia', 'Schizophrenia'),
            ('anxiety disorder', 'Anxiety disorder'),
            ('panic disorder', 'Panic disorder'),
            ('ocd', 'Obsessive-compulsive disorder'),
            ('ptsd', 'Post-traumatic stress disorder'),
            ('substance abuse', 'Substance abuse disorder'),
            ('alcohol dependence', 'Alcohol use disorder'),
            ('drug abuse', 'Drug use disorder'),
        ]
        
        for condition, label in psychiatric_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== RHEUMATOLOGIC CONDITIONS ==========
        rheumatologic_conditions = [
            ('rheumatoid arthritis', 'Rheumatoid arthritis'),
            ('ra', 'Rheumatoid arthritis'),
            ('systemic lupus erythematosus', 'Systemic lupus erythematosus'),
            ('sle', 'Systemic lupus erythematosus'),
            ('lupus', 'Systemic lupus erythematosus'),
            ('scleroderma', 'Scleroderma'),
            ('sjögren syndrome', 'Sjögren syndrome'),
            ('vasculitis', 'Vasculitis'),
            ('temporal arteritis', 'Temporal arteritis'),
            ('polymyalgia rheumatica', 'Polymyalgia rheumatica'),
            ('gout', 'Gout'),
            ('osteoarthritis', 'Osteoarthritis'),
        ]
        
        for condition, label in rheumatologic_conditions:
            if condition in notes_lower:
                risk_factors.append(label)
        
        # ========== MEDICATIONS INDICATING RISK ==========
        medications = [
            ('warfarin', 'Anticoagulation therapy'),
            ('coumadin', 'Anticoagulation therapy'),
            ('apixaban', 'Novel anticoagulant'),
            ('dabigatran', 'Novel anticoagulant'),
            ('rivaroxaban', 'Novel anticoagulant'),
            ('edoxaban', 'Novel anticoagulant'),
            ('heparin', 'Anticoagulation therapy'),
            ('enoxaparin', 'Low molecular weight heparin'),
            ('lovenox', 'Low molecular weight heparin'),
            ('aspirin', 'Antiplatelet therapy'),
            ('clopidogrel', 'Antiplatelet therapy'),
            ('plavix', 'Antiplatelet therapy'),
            ('ticagrelor', 'Antiplatelet therapy'),
            ('prasugrel', 'Antiplatelet therapy'),
            ('insulin', 'Insulin-dependent diabetes'),
            ('metformin', 'Oral diabetes medication'),
            ('sulfonylurea', 'Diabetes medication'),
            ('corticosteroid', 'Chronic corticosteroid use'),
            ('prednisone', 'Chronic corticosteroid use'),
            ('immunosuppressant', 'Immunosuppressed'),
            ('chemotherapy', 'Active chemotherapy'),
            ('lithium', 'Psychiatric medication'),
            ('antipsychotic', 'Psychiatric medication'),
            ('antidepressant', 'Psychiatric medication'),
            ('beta blocker', 'Cardiac medication'),
            ('acei', 'Cardiac medication'),
            ('arb', 'Cardiac medication'),
            ('statin', 'Lipid-lowering therapy'),
            ('nitrate', 'Cardiac medication'),
            ('digoxin', 'Cardiac glycoside'),
            ('diuretic', 'Diuretic use'),
            ('nsaid', 'NSAID use'),
            ('opiate', 'Opioid use'),
            ('opioid', 'Opioid dependency'),
        ]
        
        for med, label in medications:
            if med in notes_lower:
                risk_factors.append(label)
        
        # ========== LIFESTYLE RISK FACTORS ==========
        lifestyle_factors = [
            ('smoking', 'Active smoker'),
            ('tobacco', 'Tobacco use'),
            ('alcohol', 'Alcohol use'),
            ('heavy alcohol', 'Heavy alcohol use'),
            ('drug use', 'Substance use'),
            ('sedentary', 'Sedentary lifestyle'),
            ('obesity', 'Obesity'),
            ('overweight', 'Overweight'),
        ]
        
        for factor, label in lifestyle_factors:
            if factor in notes_lower:
                risk_factors.append(label)
        
        return list(set(risk_factors))

    @staticmethod
    def generate_icd_codes(notes: str) -> str:
        """Generate ICD-10 codes based on clinical content - COMPREHENSIVE DATABASE"""
        codes = []
        notes_lower = notes.lower()
        
        # COMPREHENSIVE ICD-10 mapping for common conditions
        icd_mapping = {
            # ========== SYMPTOMS & SIGNS ==========
            'chest pain': 'R07.9',
            'chest discomfort': 'R07.9',
            'angina': 'I20.9',
            'dyspnea': 'R06.02',
            'shortness of breath': 'R06.02',
            'difficulty breathing': 'R06.02',
            'wheezing': 'R06.02',
            'cough': 'R05.9',
            'productive cough': 'R05.9',
            'hemoptysis': 'R04.2',
            'fever': 'R50.9',
            'high fever': 'R50.9',
            'hypothermia': 'R68.0',
            'fatigue': 'R53.83',
            'weakness': 'R53.1',
            'dizziness': 'R42',
            'vertigo': 'H81.93',
            'syncope': 'R55.9',
            'fainting': 'R55.9',
            'presyncope': 'R55.1',
            'headache': 'R51.9',
            'severe headache': 'R51.9',
            'migraine': 'G43.909',
            'abdominal pain': 'R10.9',
            'severe abdominal pain': 'R10.9',
            'back pain': 'M54.5',
            'lower back pain': 'M54.5',
            'neck pain': 'M54.2',
            'joint pain': 'M25.5',
            'muscle pain': 'M79.1',
            'nausea': 'R11.0',
            'vomiting': 'R11.10',
            'diarrhea': 'K59.1',
            'constipation': 'K59.0',
            'jaundice': 'R17',
            'pallor': 'R23.1',
            'cyanosis': 'R23.0',
            'edema': 'R60.9',
            'swelling': 'R60.9',
            'rash': 'R21',
            'itching': 'L29.9',
            'insomnia': 'G47.00',
            'sleep disturbance': 'G47.9',
            'anxiety': 'R45.1',
            'depression': 'F32.9',
            'confusion': 'R41.0',
            'disorientation': 'R41.0',
            'memory loss': 'R41.1',
            
            # ========== CARDIAC CONDITIONS ==========
            'myocardial infarction': 'I21.9',
            'heart attack': 'I21.9',
            'acute myocardial infarction': 'I21.9',
            'ami': 'I21.9',
            'acute coronary syndrome': 'I24.9',
            'acs': 'I24.9',
            'unstable angina': 'I20.0',
            'nstemi': 'I21.9',
            'stemi': 'I21.9',
            'st elevation': 'I21.9',
            'arrhythmia': 'I49.9',
            'atrial fibrillation': 'I48.91',
            'afib': 'I48.91',
            'heart failure': 'I50.9',
            'chf': 'I50.9',
            'congestive heart failure': 'I50.9',
            'cardiomyopathy': 'I42.9',
            'myocarditis': 'I40.9',
            'pericarditis': 'I30.9',
            'endocarditis': 'I39',
            'valvular heart disease': 'I36.9',
            'hypertension': 'I10',
            'hypertensive': 'I10',
            'high blood pressure': 'I10',
            'bradycardia': 'R00.1',
            'tachycardia': 'R00.0',
            'hypotension': 'I95.9',
            'low blood pressure': 'I95.9',
            'shock': 'R57.9',
            'cardiogenic shock': 'R57.0',
            'pulmonary embolism': 'I26.99',
            'pe': 'I26.99',
            'deep vein thrombosis': 'I82.90',
            'dvt': 'I82.90',
            'aortic aneurysm': 'I71.9',
            'aortic dissection': 'I71.00',
            'thrombosis': 'I82.90',
            
            # ========== RESPIRATORY CONDITIONS ==========
            'pneumonia': 'J18.9',
            'aspiration pneumonia': 'J69.0',
            'bacterial pneumonia': 'J15.9',
            'viral pneumonia': 'J12.9',
            'community acquired pneumonia': 'J18.9',
            'cap': 'J18.9',
            'hospital acquired pneumonia': 'J15.9',
            'ventilator associated pneumonia': 'J95.851',
            'vap': 'J95.851',
            'pneumonitis': 'J84.10',
            'pulmonary edema': 'J81.1',
            'acute respiratory distress syndrome': 'J80',
            'ards': 'J80',
            'asthma': 'J45.901',
            'copd': 'J44.9',
            'emphysema': 'J43.9',
            'chronic bronchitis': 'J42',
            'bronchitis': 'J20.9',
            'acute bronchitis': 'J20.9',
            'bronchiectasis': 'J47.9',
            'cystic fibrosis': 'E84.9',
            'pulmonary fibrosis': 'J84.1',
            'idiopathic pulmonary fibrosis': 'J84.10',
            'ipf': 'J84.10',
            'pulmonary hypertension': 'I27.9',
            'pulmonary hemorrhage': 'J94.2',
            'hemoptysis': 'R04.2',
            'pleural effusion': 'J91.8',
            'pneumothorax': 'J93.9',
            'tension pneumothorax': 'J93.0',
            'atelectasis': 'J98.11',
            'stridor': 'R06.02',
            'laryngitis': 'J04.0',
            'epiglottitis': 'J05.10',
            
            # ========== GASTROINTESTINAL CONDITIONS ==========
            'gastroesophageal reflux': 'K21.9',
            'gerd': 'K21.9',
            'peptic ulcer': 'K27.9',
            'ulcer': 'K27.9',
            'gastroparesis': 'K31.84',
            'acute gastroenteritis': 'A09',
            'gastroenteritis': 'A09',
            'acute pancreatitis': 'K85.9',
            'pancreatitis': 'K85.9',
            'cholecystitis': 'K81.9',
            'cholangitis': 'K83.0',
            'appendicitis': 'K37',
            'acute appendicitis': 'K37',
            'diverticulitis': 'K57.92',
            'inflammatory bowel disease': 'K50.90',
            'ibd': 'K50.90',
            'ulcerative colitis': 'K51.90',
            'crohns disease': 'K50.90',
            'irritable bowel syndrome': 'K58.9',
            'ibs': 'K58.9',
            'bowel obstruction': 'K56.69',
            'paralytic ileus': 'K56.0',
            'toxic megacolon': 'K59.3',
            'celiac disease': 'K90.0',
            'gastric cancer': 'C16.9',
            'colorectal cancer': 'C18.9',
            'hepatocellular carcinoma': 'C22.0',
            'liver cirrhosis': 'K74.60',
            'hepatitis': 'K75.9',
            'fatty liver': 'K76.0',
            'nafld': 'K76.0',
            'portal hypertension': 'K76.6',
            'variceal bleeding': 'K92.0',
            'melena': 'K92.1',
            'hematochezia': 'K92.0',
            'acute liver failure': 'K72.00',
            'encephalopathy': 'G92',
            'hepatic encephalopathy': 'K72.90',
            
            # ========== ENDOCRINE CONDITIONS ==========
            'diabetes mellitus': 'E11.9',
            'diabetes': 'E11.9',
            'type 1 diabetes': 'E10.9',
            'type 2 diabetes': 'E11.9',
            'diabetic ketoacidosis': 'E10.10',
            'dka': 'E10.10',
            'hyperglycemia': 'R73.9',
            'hypoglycemia': 'E16.2',
            'thyroiditis': 'E06.9',
            'hashimoto': 'E06.3',
            'hypothyroidism': 'E03.9',
            'hyperthyroidism': 'E05.90',
            'graves disease': 'E05.00',
            'thyroid cancer': 'C73',
            'adrenal insufficiency': 'E27.1',
            'addisons disease': 'E27.1',
            'cushings syndrome': 'E24.9',
            'pcos': 'E28.2',
            
            # ========== RENAL/URINARY CONDITIONS ==========
            'chronic kidney disease': 'N18.3',
            'ckd': 'N18.3',
            'end stage renal disease': 'N18.6',
            'esrd': 'N18.6',
            'acute kidney injury': 'N17.9',
            'aki': 'N17.9',
            'renal failure': 'N19',
            'glomerulonephritis': 'N05.9',
            'nephrotic syndrome': 'N04.9',
            'nephritic syndrome': 'N05.0',
            'pyelonephritis': 'N10',
            'acute pyelonephritis': 'N10',
            'cystitis': 'N39.0',
            'urinary tract infection': 'N39.0',
            'uti': 'N39.0',
            'urosepsis': 'R65.20',
            'urinary retention': 'R33.9',
            'hematuria': 'R31.9',
            'proteinuria': 'R80.8',
            'polycystic kidney disease': 'Q61.3',
            
            # ========== NEUROLOGICAL CONDITIONS ==========
            'stroke': 'I63.9',
            'acute ischemic stroke': 'I63.9',
            'cerebral infarction': 'I63.9',
            'intracranial hemorrhage': 'I61.9',
            'subarachnoid hemorrhage': 'I60.9',
            'sh': 'I60.9',
            'epidural hematoma': 'S06.1',
            'subdural hematoma': 'S06.2',
            'transient ischemic attack': 'G45.9',
            'tia': 'G45.9',
            'seizure': 'R56.9',
            'first seizure': 'R56.9',
            'status epilepticus': 'G40.901',
            'epilepsy': 'G40.909',
            'meningitis': 'G03.9',
            'bacterial meningitis': 'G00.9',
            'viral meningitis': 'G03.0',
            'encephalitis': 'G04.90',
            'parkinson disease': 'G20',
            'alzheimers disease': 'G30.9',
            'dementia': 'G30.9',
            'multiple sclerosis': 'G35',
            'ms': 'G35',
            'myasthenia gravis': 'G70.00',
            'guillain barre': 'G61.0',
            'gbs': 'G61.0',
            'neuropathy': 'G64',
            'polyneuropathy': 'G62.9',
            'spinal cord compression': 'G99.2',
            'cauda equina syndrome': 'G83.4',
            'paralysis': 'G83.9',
            'hemiplegia': 'G81.90',
            'paraplegia': 'G82.20',
            'quadriplegia': 'G82.50',
            
            # ========== HEMATOLOGIC CONDITIONS ==========
            'anemia': 'D64.9',
            'iron deficiency anemia': 'D50.9',
            'vitamin b12 deficiency': 'D51.9',
            'folate deficiency': 'D52.9',
            'sickle cell disease': 'D57.1',
            'thalassemia': 'D56.9',
            'hemolytic anemia': 'D58.9',
            'pancytopenia': 'D61.818',
            'thrombocytopenia': 'D69.6',
            'hemophilia': 'D66',
            'von willebrand disease': 'D68.0',
            'disseminated intravascular coagulation': 'D65',
            'dic': 'D65',
            'leukemia': 'C95.90',
            'acute leukemia': 'C95.00',
            'all': 'C91.00',
            'aml': 'C92.00',
            'chronic myeloid leukemia': 'C92.10',
            'cml': 'C92.10',
            'lymphoma': 'C85.90',
            'hodgkin lymphoma': 'C81.90',
            'non hodgkin lymphoma': 'C85.90',
            'multiple myeloma': 'C90.00',
            'acute leukostasis': 'D76.3',
            
            # ========== INFECTIOUS DISEASE ==========
            'sepsis': 'A41.9',
            'severe sepsis': 'R65.21',
            'septic shock': 'R65.21',
            'endocarditis': 'I33.0',
            'osteomyelitis': 'M86.9',
            'arthritis': 'M19.90',
            'hiv': 'B20',
            'aids': 'B20',
            'tuberculosis': 'A15.0',
            'tb': 'A15.0',
            'hepatitis a': 'A15.0',
            'hepatitis b': 'B18.1',
            'hepatitis c': 'B18.2',
            'influenza': 'J11.00',
            'covid19': 'U07.1',
            'coronavirus': 'U07.1',
            
            # ========== NEOPLASMS ==========
            'cancer': 'C80.1',
            'malignancy': 'C80.1',
            'lung cancer': 'C34.90',
            'breast cancer': 'C50.91',
            'colon cancer': 'C18.9',
            'prostate cancer': 'C61',
            'ovarian cancer': 'C56.9',
            'pancreatic cancer': 'C25.9',
            'gastric cancer': 'C16.9',
            'hepatocellular carcinoma': 'C22.0',
            'renal cell carcinoma': 'C64.9',
            'bladder cancer': 'C67.9',
            'melanoma': 'C43.9',
            'squamous cell carcinoma': 'C44.92',
            'basal cell carcinoma': 'C44.91',
            'lymphoma': 'C85.90',
            'leukemia': 'C95.90',
            'metastatic disease': 'C79.9',
            'bone metastases': 'C79.51',
            'brain metastases': 'C79.31',
            
            # ========== COMORBIDITIES & CHRONIC CONDITIONS ==========
            'obesity': 'E66.9',
            'overweight': 'E66.3',
            'hypertension': 'I10',
            'hyperlipidemia': 'E78.5',
            'metabolic syndrome': 'E88.81',
        }
        
        for condition, code in icd_mapping.items():
            if condition in notes_lower:
                if code not in codes:
                    codes.append(code)
        
        return ', '.join(codes) if codes else 'R69.9'

    @staticmethod
    def calculate_confidence_score(notes: str, risk_words: List[str]) -> int:
        """Calculate confidence score of summarization"""
        score = 50
        
        # Length factor
        if len(notes) > 200:
            score += 10
        if len(notes) > 500:
            score += 10
        
        # Structured data factor
        structured_keywords = ['vital signs', 'physical exam', 'assessment', 'plan', 'impression']
        structured_count = sum(1 for keyword in structured_keywords if keyword in notes.lower())
        score += min(structured_count * 5, 15)
        
        # Risk detection factor
        if risk_words:
            score += min(len(risk_words) * 2, 10)
        
        return min(score, 95)
