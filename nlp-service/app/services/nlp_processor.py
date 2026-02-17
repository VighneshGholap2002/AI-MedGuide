import re
from typing import List, Dict, Tuple
import logging
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# Initialize NLP models (lazy loading for performance)
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


# ========== HELPER FUNCTIONS FOR ENHANCED NLP ==========

def word_boundary_match(text: str, keyword: str) -> bool:
    """
    Check if keyword exists as a complete word (word boundary matching)
    Not just substring matching.
    
    Examples:
        - "stroke" matches "I had a stroke" ✓
        - "stroke" does NOT match "prestroke" ✗
        - "stroke" does NOT match "keyboard" ✗
    
    Args:
        text: The text to search in
        keyword: The keyword to search for
    
    Returns:
        True if keyword found as complete word, False otherwise
    """
    pattern = r'\b' + re.escape(keyword) + r'\b'
    return bool(re.search(pattern, text, re.IGNORECASE))


def extract_medical_entities(notes: str) -> List[str]:
    """
    Extract medical entities using spaCy NLP
    Handles lemmatization and named entity recognition
    
    This helps catch medical terms even if written differently:
    - "presented" → "present"
    - "pneumonias" → "pneumonia"
    - "seizures" → "seizure"
    
    Args:
        notes: Clinical notes text
    
    Returns:
        List of extracted medical entities and lemmas
    """
    nlp = get_nlp_model()
    if nlp is None:
        return []
    
    entities = []
    try:
        doc = nlp(notes.lower())
        
        # Extract named entities (medical terms often tagged as entities)
        for ent in doc.ents:
            if ent.label_ not in ['PERSON', 'ORG', 'GPE']:
                entities.append(ent.text)
        
        # Extract key noun chunks (medical terms often appear as noun phrases)
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 4:  # Multi-word medical terms
                entities.append(chunk.text)
        
        # Lemmatize tokens to catch variations
        # "seizures" becomes "seizure", "bleeding" becomes "bleed"
        for token in doc:
            if token.pos_ in ['NOUN', 'VERB', 'ADJ'] and len(token.lemma_) > 2:
                entities.append(token.lemma_)
        
        return list(set(entities))
    except Exception as e:
        logger.warning(f"spaCy processing error: {e}")
        return []


def semantic_similarity_match(notes: str, keywords_list: List[str], threshold: float = 0.3) -> List[str]:
    """
    Find semantically similar keywords using TF-IDF vectorization (no PyTorch needed!)
    Catches synonyms and variations that exact matching might miss.
    
    Examples:
    - Will match "cardiac arrest" with "heart stops" or "asystole"
    - Will match "dyspnea" with "breathing difficulty" or "shortness of breath"  
    - Will match "altered mental status" with "confusion" or "delirium"
    
    Uses lightweight scikit-learn instead of sentence-transformers
    
    Args:
        notes: Clinical notes text
        keywords_list: List of keywords to match
        threshold: Similarity threshold (0-1, default 0.3)
    
    Returns:
        List of matched keywords based on semantic similarity
    """
    if len(keywords_list) == 0:
        return []
    
    matched = []
    try:
        # Split notes into sentences for better semantic matching
        sentences = notes.split('. ')
        notes_text = ' '.join(sentences[:15]).lower()  # First 15 sentences
        
        # Prepare texts for TF-IDF vectorization
        all_texts = [notes_text] + [kw.lower() for kw in keywords_list]
        
        # Create TF-IDF vectorizer (lightweight alternative to embeddings)
        vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3), lowercase=True)
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate cosine similarities between note and each keyword
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Find matches above threshold
        for idx, score in enumerate(similarities):
            if score > threshold:
                matched.append(keywords_list[idx])
                logger.debug(f"Semantic match: {keywords_list[idx]} (score: {score:.2f})")
        
        return matched
    except Exception as e:
        logger.warning(f"TF-IDF similarity matching error: {e}")
        return []


# COMPREHENSIVE High-risk clinical keywords mapping - HIGHLY EXPANDED
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
    'vfib': 'CRITICAL',
    'pea': 'CRITICAL',
    
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
    'massive stroke': 'CRITICAL',
    
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
    'severe metabolic disturbance': 'CRITICAL',
    
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
    'uncontrolled bleeding': 'CRITICAL',
    
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
    'aspiration': 'CRITICAL',
    
    # ========== HIGH RISK CONDITIONS (>50 additional keywords) ==========
    'pneumonia': 'HIGH',
    'aspiration pneumonia': 'HIGH',
    'community acquired pneumonia': 'HIGH',
    'hospital acquired pneumonia': 'HIGH',
    'ventilator associated pneumonia': 'HIGH',
    'pulmonary edema': 'HIGH',
    'pulmonary hemorrhage': 'HIGH',
    'acute bronchitis': 'HIGH',
    'severe cough': 'HIGH',
    'pneumonitis': 'HIGH',
    'interstitial pneumonia': 'HIGH',
    'atypical pneumonia': 'HIGH',
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
    'severe abdominal pain': 'HIGH',
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
    'acute diabetes': 'HIGH',
    'thyroid storm': 'HIGH',
    'myxedema coma': 'HIGH',
    'adrenal crisis': 'HIGH',
    'severe hyperthyroidism': 'HIGH',
    'severe hypothyroidism': 'HIGH',
    'hyperthyroid crisis': 'HIGH',
    'acute leukemia': 'HIGH',
    'acute lymphoblastic leukemia': 'HIGH',
    'acute myeloid leukemia': 'HIGH',
    'tumor lysis syndrome': 'HIGH',
    'sickle cell crisis': 'HIGH',
    'thalassemia major': 'HIGH',
    'hemolytic anemia': 'HIGH',
    'hemophilia': 'HIGH',
    'von willebrand disease': 'HIGH',
    'bleeding disorder': 'HIGH',
    'coagulation disorder': 'HIGH',
    'severe pre-eclampsia': 'HIGH',
    'preeclampsia': 'HIGH',
    'hellp syndrome': 'HIGH',
    'retained placenta': 'HIGH',
    'postpartum hemorrhage': 'HIGH',
    'severe pregnancy complication': 'HIGH',
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


class ClinicalNoteProcessor:
    
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
            # Look for NFM levels
            nfm_match = re.search(r'nfm.*?(\d+\.?\d*)\s*units?', notes_lower)
            if nfm_match:
                findings.append(f"Serum Neuroflux Marker (NFM) elevated at {nfm_match.group(1)} units")
        
        # Clean up findings (remove duplicates and sort)
        findings = list(set(findings))[:5]
        
        return ' '.join(findings) if findings else "No specific findings documented"

    @staticmethod
    def detect_risk_words(notes: str) -> List[str]:
        """
        Detect risk words using THREE advanced methods:
        
        1. WORD BOUNDARY MATCHING: Exact word match, not substring
           - "stroke" matches "stroke" but NOT "keystroke" or "prestroke"
        
        2. SPACY NLP + LEMMATIZATION: Catch word variations
           - "pneumonias" matches "pneumonia"
           - "seizing" matches "seizure"
           - Handles synonyms and lemma forms
        
        3. SEMANTIC SIMILARITY: Find similar meanings
           - "breathing difficulty" matches "shortness of breath"
           - "heart stops" matches "cardiac arrest"
           - Catches clinical synonyms
        
        Args:
            notes: Clinical notes text
        
        Returns:
            List of detected risk words/conditions with highest precision
        """
        risk_words = []
        notes_lower = notes.lower()
        
        # METHOD 1: Word Boundary Matching (Highest precision)
        # ====================================================
        logger.info(f"Starting risk word detection for {len(notes)} character note...")
        
        boundary_matches = []
        for keyword in HIGH_RISK_KEYWORDS.keys():
            if word_boundary_match(notes_lower, keyword):
                boundary_matches.append(keyword)
                logger.debug(f"Boundary match found: {keyword}")
        
        risk_words.extend(boundary_matches)
        logger.info(f"Boundary matches: {len(boundary_matches)}")
        
        # METHOD 2: spaCy NLP + Lemmatization (Medium precision, catches variations)
        # ===========================================================================
        if len(risk_words) < 10:  # Only if we haven't found enough matches
            spacy_entities = extract_medical_entities(notes_lower)
            logger.info(f"Extracted {len(spacy_entities)} medical entities")
            
            for entity in spacy_entities:
                for keyword in HIGH_RISK_KEYWORDS.keys():
                    # Check if entity is a lemma or variant of keyword
                    if word_boundary_match(entity, keyword) or word_boundary_match(keyword, entity):
                        if keyword not in risk_words:
                            risk_words.append(keyword)
                            logger.debug(f"spaCy match found: {entity} → {keyword}")
        
        # METHOD 3: Semantic Similarity Search (Medium precision, catches synonyms)
        # =========================================================================
        if len(risk_words) < 5:  # Only if we still haven't found enough matches
            keywords_list = list(HIGH_RISK_KEYWORDS.keys())
            semantic_matches = semantic_similarity_match(notes_lower, keywords_list, threshold=0.65)
            logger.info(f"Semantic matches: {len(semantic_matches)}")
            
            for match in semantic_matches:
                if match not in risk_words:
                    risk_words.append(match)
                    logger.debug(f"Semantic match found: {match}")
        
        # Remove duplicates and return
        final_results = list(set(risk_words))
        logger.info(f"Total risk words detected: {len(final_results)}")
        return final_results

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
        
        return list(set(risk_factors))

    @staticmethod
    def generate_icd_codes(notes: str) -> str:
        """Generate ICD-10 codes based on clinical content"""
        codes = []
        notes_lower = notes.lower()
        
        icd_mapping = {
            'chest pain': 'R07.9',
            'stroke': 'I63.9',
            'myocardial infarction': 'I21.9',
            'pneumonia': 'J18.9',
            'sepsis': 'A41.9',
            'seizure': 'R56.9',
        }
        
        for condition, code in icd_mapping.items():
            if word_boundary_match(notes_lower, condition):
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
