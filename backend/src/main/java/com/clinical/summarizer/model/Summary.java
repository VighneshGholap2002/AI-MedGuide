package com.clinical.summarizer.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Summary {
    private String chiefComplaint;
    private String keyFindings;
    private String assessment;
    private List<String> recommendations;
    private String icdCodes;
}
