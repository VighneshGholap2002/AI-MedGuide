package com.clinical.summarizer.service;

import com.clinical.summarizer.model.PatientCase;
import com.clinical.summarizer.model.Summary;
import com.clinical.summarizer.repository.PatientCaseRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
@Slf4j
public class SummarizationService {

    private final PatientCaseRepository patientCaseRepository;
    private final WebClient webClient;

    @Value("${nlp-service.url}")
    private String nlpServiceUrl;

    @Value("${nlp-service.timeout}")
    private int timeout;

    public PatientCase createCase(PatientCase patientCase) {
        patientCase.setCreatedAt(LocalDateTime.now());
        patientCase.setUpdatedAt(LocalDateTime.now());
        return patientCaseRepository.save(patientCase);
    }

    public PatientCase summarizeCase(String caseId) {
        PatientCase patientCase = patientCaseRepository.findById(caseId)
                .orElseThrow(() -> new RuntimeException("Case not found: " + caseId));

        try {
            // Call NLP service for summarization
            SummarizationRequest request = SummarizationRequest.builder()
                    .caseId(caseId)
                    .clinicalNotes(patientCase.getClinicalNotes())
                    .patientAge(patientCase.getPatientAge())
                    .gender(patientCase.getGender())
                    .build();

            SummarizationResponse response = callNlpService(request)
                    .block();

            if (response != null) {
                patientCase.setSummary(response.getSummary());
                patientCase.setRiskFactors(response.getRiskFactors());
                patientCase.setRiskWords(response.getRiskWords());
                patientCase.setConfidenceScore(response.getConfidenceScore());
                patientCase.setMetadata(response.getMetadata());
                patientCase.setUpdatedAt(LocalDateTime.now());

                return patientCaseRepository.save(patientCase);
            }
        } catch (Exception e) {
            log.error("Error summarizing case: {}", caseId, e);
            throw new RuntimeException("Failed to summarize case", e);
        }

        return patientCase;
    }

    private Mono<SummarizationResponse> callNlpService(SummarizationRequest request) {
        return webClient.post()
                .uri(nlpServiceUrl + "/api/v1/summarize")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(SummarizationResponse.class)
                .timeout(java.time.Duration.ofMillis(timeout));
    }

    public List<PatientCase> getAllCases() {
        return patientCaseRepository.findAll();
    }

    public PatientCase getCaseById(String id) {
        return patientCaseRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Case not found: " + id));
    }

    public PatientCase updateCase(String id, PatientCase patientCase) {
        PatientCase existing = getCaseById(id);
        existing.setCaseTitle(patientCase.getCaseTitle());
        existing.setClinicalNotes(patientCase.getClinicalNotes());
        existing.setPatientAge(patientCase.getPatientAge());
        existing.setGender(patientCase.getGender());
        existing.setUpdatedAt(LocalDateTime.now());
        return patientCaseRepository.save(existing);
    }

    public void deleteCase(String id) {
        patientCaseRepository.deleteById(id);
    }

    public Map<String, String> getHighRiskKeywords() {
        Map<String, String> riskKeywords = new HashMap<>();
        riskKeywords.put("chest pain", "CRITICAL");
        riskKeywords.put("shortness of breath", "CRITICAL");
        riskKeywords.put("acute myocardial infarction", "CRITICAL");
        riskKeywords.put("stroke", "CRITICAL");
        riskKeywords.put("sepsis", "CRITICAL");
        riskKeywords.put("diabetic ketoacidosis", "HIGH");
        riskKeywords.put("hypertensive crisis", "HIGH");
        riskKeywords.put("pulmonary embolism", "HIGH");
        riskKeywords.put("severe infection", "HIGH");
        return riskKeywords;
    }
}
