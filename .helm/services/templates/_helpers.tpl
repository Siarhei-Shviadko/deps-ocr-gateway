{{/*
Expand the name of the chart.
*/}}
{{- define "deps-ocr.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "deps-ocr.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "deps-ocr.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "deps-ocr.labels" -}}
helm.sh/chart: {{ include "deps-ocr.chart" . }}
{{ include "deps-ocr.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{/*
#-------------------------------------------------------
# This selector shoul use when will delete ocr-api
# If we use oar-api and ocr-api-gateway with one service should use hardcode
# {{- define "deps-ocr.selectorLabels" -}}
# app.kubernetes.io/name: {{ include "deps-ocr.name" . }}
# app.kubernetes.io/instance: {{ .Release.Name }}
# {{- end }}
#-------------------------------------------------------
*/}}
{{- define "deps-ocr.selectorLabels" -}}
app.kubernetes.io/name: {{ include "deps-ocr.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "deps-ocr-api-gateway-aws-textract.selectorLabels" -}}
app.kubernetes.io/name: 'deps-ocr-api-gateway-aws-textract'
app.kubernetes.io/instance: 'deps-ocr-api-gateway-aws-textract'
{{- end }}

{{- define "deps-ocr-api-gateway-azure-form-recognizer.selectorLabels" -}}
app.kubernetes.io/name: 'deps-ocr-api-gateway-azure-form-recognizer'
app.kubernetes.io/instance: 'deps-ocr-api-gateway-azure-form-recognizer'
{{- end }}

{{- define "deps-ocr-api-gateway-gcp-vision.selectorLabels" -}}
app.kubernetes.io/name: 'deps-ocr-api-gateway-gcp-vision'
app.kubernetes.io/instance: 'deps-ocr-api-gateway-gcp-vision'
{{- end }}

{{- define "deps-ocr-api-gateway-tesseract.selectorLabels" -}}
app.kubernetes.io/name: 'deps-ocr-api-gateway-tesseract'
app.kubernetes.io/instance: 'deps-ocr-api-gateway-tesseract'
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "deps-ocr.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "deps-ocr.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
