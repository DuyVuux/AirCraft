import React, { useRef, useEffect, useState, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import type { editor } from 'monaco-editor';
import type { InputData } from '@/types/input';
import { validateJSON } from '@/utils/jsonValidator';
import { AIRCRAFT_TYPES } from '@/types/aircraft';
import { ROLES } from '@/types/employee';
import './JsonEditor.css';

interface JsonMonacoEditorProps {
  onDataChange?: (data: InputData | null) => void;
  initialData?: InputData | null;
}

const LOCATION_TYPES = ['GATE', 'HANGAR', 'APRON', 'HUB', 'REST_AREA'];
const TASK_CODES = [
  'TASK_TIRE_CHECK',
  'TASK_OIL_CHANGE',
  'TASK_ENGINE_INSPECT',
  'TASK_CLEANING',
  'TASK_LOADING',
  'TASK_UNLOADING',
  'TASK_REFUEL',
  'TASK_PUSHBACK',
];

// Sample template based on input_sample (2).json
const SAMPLE_TEMPLATE = `{
  "trackingId": "PLAN-2024-12-05-001",
  "aircrafts": [
    {
      "aircraftId": "VN-A320",
      "aType": {
        "id": "A320",
        "desc": "Airbus A320"
      },
      "location": {
        "locationId": "GATE-01",
        "locationType": "GATE",
          "longitude": 105.8067,
          "latitude": 21.2144
      },
      "timeWindow": {
        "start": "2024-12-05T08:00:00Z",
        "end": "2024-12-05T12:00:00Z"
      },
      "requiredTasks": [
        {
          "taskCode": "TASK_TIRE_CHECK",
          "minLevel": 1
        },
        {
          "taskCode": "TASK_OIL_CHANGE",
          "minLevel": 2
        }
      ]
    }
  ],
  "hubs": [
    {
      "hubId": "HUB_01",
      "location": {
        "locationId": "REST_AREA_A",
        "locationType": "HUB",
        "longitude": 106.6650,
        "latitude": 10.8200
      }
    }
  ],
  "employees": [
    {
      "employeeId": "EMP_001",
      "eType": {
        "role": "MECHANIC",
        "level": 1
      },
      "workingTimes": [
        {
          "start": "2024-12-05T07:00:00Z",
          "end": "2024-12-05T17:00:00Z"
        }
      ],
      "breakDuration": 3600,
      "fixedBreakTimes": [
        {
          "start": "2024-12-05T12:00:00Z",
          "end": "2024-12-05T13:00:00Z"
        }
      ]
    }
  ],
  "matrixConfigs": {
    "distanceMatrix": [
      {
        "srcCode": "GATE-01",
        "destCode": "HANGAR-02",
        "travelTime": 900
      }
    ],
    "timeMatrix": [
      {
        "taskCode": "TASK_TIRE_CHECK",
        "role": "MECHANIC",
        "level": 1,
        "aircraftId": "VN-A320",
        "timeProcess": 1800
      }
    ]
  }
}`;

const JsonMonacoEditor: React.FC<JsonMonacoEditorProps> = ({
  onDataChange,
  initialData,
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const validationTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const [jsonValue, setJsonValue] = useState<string>(
    initialData ? JSON.stringify(initialData, null, 2) : SAMPLE_TEMPLATE
  );
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [isValid, setIsValid] = useState<boolean>(false);
  const isInitialMountRef = useRef(true);

  useEffect(() => {
    if (initialData && isInitialMountRef.current) {
      const jsonString = JSON.stringify(initialData, null, 2);
      setJsonValue(jsonString);
      isInitialMountRef.current = false;
    }
  }, [initialData]);

  const handleEditorDidMount = (editor: editor.IStandaloneCodeEditor, monaco: any) => {
    editorRef.current = editor;

    // Configure autocomplete
    if (monaco) {
      // Register completion provider
      monaco.languages.registerCompletionItemProvider('json', {
        provideCompletionItems: (model: editor.ITextModel, position: { lineNumber: number; column: number }) => {
          const word = model.getWordUntilPosition(position);
          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn,
          };

          const textUntilPosition = model.getValueInRange({
            startLineNumber: 1,
            startColumn: 1,
            endLineNumber: position.lineNumber,
            endColumn: position.column,
          });

          const suggestions: any[] = [];

          // Suggest based on context
          if (textUntilPosition.includes('"aType"') && textUntilPosition.includes('"id"')) {
            Object.keys(AIRCRAFT_TYPES).forEach((id) => {
              suggestions.push({
                label: id,
                kind: monaco.languages.CompletionItemKind.Value,
                insertText: `"${id}"`,
                range,
                detail: AIRCRAFT_TYPES[id as keyof typeof AIRCRAFT_TYPES],
              });
            });
          }

          if (textUntilPosition.includes('"locationType"')) {
            LOCATION_TYPES.forEach((type) => {
              suggestions.push({
                label: type,
                kind: monaco.languages.CompletionItemKind.Value,
                insertText: `"${type}"`,
                range,
              });
            });
          }

          if (textUntilPosition.includes('"role"')) {
            ROLES.forEach((role) => {
              suggestions.push({
                label: role,
                kind: monaco.languages.CompletionItemKind.Value,
                insertText: `"${role}"`,
                range,
              });
            });
          }

          // Level field removed from employee model

          if (textUntilPosition.includes('"taskCode"')) {

            TASK_CODES.forEach((task) => {
              suggestions.push({
                label: task,
                kind: monaco.languages.CompletionItemKind.Value,
                insertText: `"${task}"`,
                range,
                detail: 'Task code',
              });
            });
          }

          // Suggest property names when typing in object
          if (textUntilPosition.match(/["{]\s*$/)) {
            const commonProperties = [
              { label: 'trackingId', insertText: '"trackingId": "$1"' },
              { label: 'aircrafts', insertText: '"aircrafts": [$1]' },
              { label: 'hubs', insertText: '"hubs": [$1]' },
              { label: 'employees', insertText: '"employees": [$1]' },
              { label: 'matrixConfigs', insertText: '"matrixConfigs": {$1}' },
              { label: 'aircraftId', insertText: '"aircraftId": "$1"' },
              { label: 'aType', insertText: '"aType": {$1}' },
              { label: 'location', insertText: '"location": {$1}' },
              { label: 'timeWindow', insertText: '"timeWindow": {$1}' },
              { label: 'requiredTasks', insertText: '"requiredTasks": [$1]' },
              { label: 'hubId', insertText: '"hubId": "$1"' },
              { label: 'employeeId', insertText: '"employeeId": "$1"' },
              { label: 'eType', insertText: '"eType": {$1}' },
              { label: 'workingTimes', insertText: '"workingTimes": [$1]' },
              { label: 'breakDuration', insertText: '"breakDuration": $1' },
              { label: 'fixedBreakTimes', insertText: '"fixedBreakTimes": [$1]' },
              { label: 'distanceMatrix', insertText: '"distanceMatrix": [$1]' },
              { label: 'timeMatrix', insertText: '"timeMatrix": [$1]' },
              { label: 'srcCode', insertText: '"srcCode": "$1"' },
              { label: 'destCode', insertText: '"destCode": "$1"' },
              { label: 'travelTime', insertText: '"travelTime": $1' },
              { label: 'taskCode', insertText: '"taskCode": "$1"' },
              { label: 'role', insertText: '"role": "$1"' },
              { label: 'level', insertText: '"level": $1' },
              { label: 'aircraftId', insertText: '"aircraftId": "$1"' },
              { label: 'timeProcess', insertText: '"timeProcess": $1' },
              { label: 'minLevel', insertText: '"minLevel": $1' },
              { label: 'locationId', insertText: '"locationId": "$1"' },
              { label: 'locationType', insertText: '"locationType": "$1"' },
              { label: 'longitude', insertText: '"longitude": $1' },
              { label: 'latitude', insertText: '"latitude": $1' },
              { label: 'start', insertText: '"start": "$1"' },
              { label: 'end', insertText: '"end": "$1"' },
              { label: 'id', insertText: '"id": "$1"' },
              { label: 'desc', insertText: '"desc": "$1"' },
            ];

            commonProperties.forEach((prop) => {
              suggestions.push({
                label: prop.label,
                kind: monaco.languages.CompletionItemKind.Property,
                insertText: prop.insertText,
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                range,
              });
            });
          }

          return { suggestions };
        },
      });
    }
  };

  const validateAndNotify = useCallback((jsonString: string) => {
    try {
      const parsed = JSON.parse(jsonString);
      const result = validateJSON(jsonString);
      setIsValid(result.valid);
      setValidationErrors(result.errors.map((e) => `${e.field}: ${e.message}`));
      onDataChange?.(result.valid ? (parsed as InputData) : null);
    } catch (error) {
      setIsValid(false);
      setValidationErrors([`Parse error: ${(error as Error).message}`]);
      onDataChange?.(null);
    }
  }, [onDataChange]);

  const handleEditorChange = useCallback((value: string | undefined) => {
    if (value !== undefined) {
      setJsonValue(value);

      // Debounce validation to avoid lag
      if (validationTimeoutRef.current) {
        clearTimeout(validationTimeoutRef.current);
      }

      validationTimeoutRef.current = setTimeout(() => {
        validateAndNotify(value);
      }, 500); // Wait 500ms after user stops typing
    }
  }, [validateAndNotify]);

  useEffect(() => {
    return () => {
      if (validationTimeoutRef.current) {
        clearTimeout(validationTimeoutRef.current);
      }
    };
  }, []);

  const handleLoadTemplate = useCallback(() => {
    setJsonValue(SAMPLE_TEMPLATE);
    if (editorRef.current) {
      editorRef.current.setValue(SAMPLE_TEMPLATE);
    }
    if (validationTimeoutRef.current) {
      clearTimeout(validationTimeoutRef.current);
    }
    validateAndNotify(SAMPLE_TEMPLATE);
  }, [validateAndNotify]);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setJsonValue(content);
      if (editorRef.current) {
        editorRef.current.setValue(content);
      }
      if (validationTimeoutRef.current) {
        clearTimeout(validationTimeoutRef.current);
      }
      validateAndNotify(content);
    };
    reader.readAsText(file);
  }, [validateAndNotify]);

  const handleDownload = () => {
    const blob = new Blob([jsonValue], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `input_data_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <div className="json-editor-header" style={{ marginBottom: '1rem' }}>
        <h3 className="json-editor-title">JSON Editor với Autocomplete</h3>
        <div className="json-editor-actions">
          <input
            type="file"
            accept=".json"
            style={{ display: 'none' }}
            id="json-upload-input"
            onChange={handleFileUpload}
          />
          <button
            className="json-editor-button json-editor-button-primary"
            onClick={() => document.getElementById('json-upload-input')?.click()}
            type="button"
          >
            <span className="material-symbols-outlined">upload_file</span>
            UPLOAD FILE
          </button>
          <button
            className="json-editor-button"
            onClick={handleLoadTemplate}
            type="button"
          >
            LOAD TEMPLATE
          </button>
          <button
            className="json-editor-button"
            onClick={handleDownload}
            type="button"
          >
            <span className="material-symbols-outlined">download</span>
            DOWNLOAD
          </button>
        </div>
      </div>

      <div style={{ border: '1px solid var(--border-light)', borderRadius: '0.5rem', overflow: 'hidden' }}>
        <Editor
          height="600px"
          defaultLanguage="json"
          value={jsonValue}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme="vs-dark"
          loading={<div style={{ padding: '1rem' }}>Loading editor...</div>}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            wordWrap: 'on',
            formatOnPaste: true,
            formatOnType: false, // Disable format on type to reduce lag
            tabSize: 2,
            suggestOnTriggerCharacters: true,
            quickSuggestions: {
              other: true,
              comments: false,
              strings: true,
            },
            acceptSuggestionOnCommitCharacter: true,
            acceptSuggestionOnEnter: 'on',
            snippetSuggestions: 'top',
            autoIndent: 'full',
            bracketPairColorization: { enabled: true },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            renderValidationDecorations: 'off', // Disable validation decorations to improve performance
            quickSuggestionsDelay: 100,
          }}
        />
      </div>

      {isValid && (
        <div className="json-editor-alert json-editor-alert-success" style={{ marginTop: '1rem' }}>
          ✅ JSON hợp lệ!
        </div>
      )}

      {validationErrors.length > 0 && (
        <div className="json-editor-alert json-editor-alert-error" style={{ marginTop: '1rem' }}>
          <div style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Lỗi validation:</div>
          <ul>
            {validationErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default JsonMonacoEditor;

