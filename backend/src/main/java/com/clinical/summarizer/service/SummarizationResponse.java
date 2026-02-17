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
public class SummarizationResponse {
    private String caseId;
    private Summary summary;
    private List<String> riskFactors;
    private List<String> riskWords;
    private Integer confidenceScore;
    private Map<String, Object> metadata;
}
