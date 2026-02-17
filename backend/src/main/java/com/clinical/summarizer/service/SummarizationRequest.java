package com.clinical.summarizer.service;

import com.clinical.summarizer.model.Summary;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SummarizationRequest {
    private String caseId;
    private String clinicalNotes;
    private String patientAge;
    private String gender;
}
