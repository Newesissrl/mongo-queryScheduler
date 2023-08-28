{{- /* Define the trimAfterDotLower function */ -}}
{{- define "trimAfterDotLower" -}}
  {{- $value := . -}}
  {{- $split := splitList "." $value -}}
  {{- index $split 1 | lower -}}
{{- end -}}


{{- /*
Replaces dots with underscores in a string.
Usage: {{ replaceDotsWithDashes "inputString" }}
*/ -}}
{{- define "replaceDotsWithDashes" -}}
{{- $input := . -}}
{{- $output := $input | replace "." "-" | lower  -}}
{{- $output -}}
{{- end -}}