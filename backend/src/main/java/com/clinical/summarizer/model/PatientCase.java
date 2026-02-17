package com.clinical.summarizer.model;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Document(collection = "patient_cases")
public class PatientCase {
    @Id
    private String id;
    
    private String caseTitle;
    private String patientAge;
    private String gender;
    private String clinicalNotes;
    
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime createdAt;
    
    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
    private LocalDateTime updatedAt;
    
    // Summarization results
    private Summary summary;
    private List<String> riskFactors;
    private List<String> riskWords;
    private Integer confidenceScore;
    private Map<String, Object> metadata;
}
