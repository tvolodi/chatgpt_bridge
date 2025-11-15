# REQ-503: Provider-Specific Parameters

**Registry Entry:** See `docs/01_requirements_registry.md` (Line 113)  
**Functionality Reference:** `specifications/functionality.md` Section 5.1.3  
**Document Version:** 1.0  
**Last Updated:** November 15, 2025  
**Status:** implemented  

---

## 1. Overview

### 1.1 Brief Description
Each AI provider supports different configuration parameters for fine-tuning model behavior. The system must allow users to configure provider-specific parameters like temperature, max_tokens, top_p, and others, enabling optimization of responses based on specific use cases and provider capabilities.

### 1.2 Business Value
- **Response Quality:** Fine-tune creativity, determinism, length per use case
- **Cost Optimization:** Balance quality with token usage
- **Provider Flexibility:** Leverage unique capabilities of each provider
- **Experimentation:** Compare outputs with different parameter values
- **Consistency:** Save parameter sets as templates for repeated use

---

## 2. Functional Requirements

### 2.1 Core Requirements

#### REQ-503-A: Provider-Specific Parameter Support
- **Description:** Each provider exposes different parameters
- **OpenAI Parameters:**
  - `temperature` (0.0-2.0): Creativity/randomness, default 1.0
  - `max_tokens` (1-128,000): Max response length
  - `top_p` (0.0-1.0): Nucleus sampling, default 1.0
  - `frequency_penalty` (-2.0-2.0): Reduce token repetition
  - `presence_penalty` (-2.0-2.0): Encourage new topics
  - `n` (1+): Number of completions to generate
  - `best_of` (1+): Best of N versions
  - `stop` (string or array): Stop sequences
- **Anthropic Parameters:**
  - `temperature` (0.0-1.0): Creativity/randomness, default 1.0
  - `max_tokens` (1-200,000): Max response length, required
  - `top_p` (0.0-1.0): Nucleus sampling, default 1.0
  - `top_k` (0-500): Top-k sampling, optional
  - `stop_sequences` (array): Stop sequences
  - `system` (string): System prompt override
- **Ollama Parameters:**
  - `temperature` (0.0-2.0): Creativity/randomness
  - `num_predict` (integers): Tokens to predict
  - `top_p` (0.0-1.0): Nucleus sampling
  - `top_k` (integer): Top-k sampling
  - `num_ctx` (integer): Context window size
  - `repeat_penalty` (float): Repeat penalty
  - `repeat_last_n` (integer): Last N tokens for repeat
  - `tfs_z` (float): Tail-free sampling parameter
- **Cohere Parameters:**
  - `temperature` (0.0-5.0): Creativity/randomness
  - `max_tokens` (1-4,096): Max response length
  - `p` (0.0-1.0): Nucleus sampling
  - `k` (0+): Top-k sampling
  - `frequency_penalty` (0.0-1.0): Repetition penalty
- **Acceptance Criteria:**
  - ✓ Each provider's parameters documented
  - ✓ Parameters validated per provider
  - ✓ Invalid values rejected with clear errors
  - ✓ Default values used when not specified

#### REQ-503-B: Parameter Configuration Storage
- **Description:** Store provider parameters for persistence and reuse
- **Storage Hierarchy:**
  1. **Global Defaults:** In `providers_config.json` - defaults for all users
  2. **Project-Level:** In project's `settings.json` - applies to all sessions in project
  3. **Session-Level:** In session's `metadata.json` - applies to specific session
  4. **Request-Level:** Override at message time (temporary)
- **Configuration Structure:**
  ```json
  {
    "provider_parameters": {
      "openai": {
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 1.0,
        "frequency_penalty": 0,
        "presence_penalty": 0
      },
      "anthropic": {
        "temperature": 1.0,
        "max_tokens": 1024,
        "top_p": 1.0
      }
    }
  }
  ```
- **Parameter Override Priority:**
  1. Request-level override (highest priority)
  2. Session-level settings
  3. Project-level settings
  4. Global defaults (lowest priority)
- **Acceptance Criteria:**
  - ✓ Parameters stored in correct JSON location
  - ✓ Hierarchy enforced correctly
  - ✓ Override precedence works
  - ✓ All providers' defaults specified

#### REQ-503-C: Parameter Validation and Constraints
- **Description:** Validate parameters against provider constraints
- **Validation Rules:**
  - Type checking (float, int, string, array)
  - Range checking (min/max values)
  - Enum checking (allowed values)
  - Dependency checking (e.g., top_k requires top_p)
  - Format checking (arrays, strings with special chars)
- **Provider-Specific Constraints:**
  ```json
  {
    "openai": {
      "temperature": {"type": "float", "min": 0, "max": 2, "default": 1},
      "max_tokens": {"type": "int", "min": 1, "max": 128000, "required": false},
      "top_p": {"type": "float", "min": 0, "max": 1, "default": 1},
      "n": {"type": "int", "min": 1, "max": 128, "default": 1},
      "stop": {"type": "array|string", "items": "string", "required": false}
    },
    "anthropic": {
      "temperature": {"type": "float", "min": 0, "max": 1, "default": 1},
      "max_tokens": {"type": "int", "min": 1, "max": 200000, "required": true},
      "top_p": {"type": "float", "min": 0, "max": 1, "default": 1},
      "top_k": {"type": "int", "min": 0, "required": false}
    }
  }
  ```
- **Error Handling:**
  - Out-of-range values → Clamp to valid range with warning
  - Missing required params → Use provider default or reject request
  - Invalid type → Show error, require correction
  - Unsupported param → Log warning, ignore parameter
- **Acceptance Criteria:**
  - ✓ All parameters validated before use
  - ✓ Invalid params handled gracefully
  - ✓ User receives clear error messages
  - ✓ No invalid requests sent to providers

#### REQ-503-D: Parameter Settings Page UI
- **Description:** UI for configuring parameters per provider
- **Location:** Settings page → "Provider Parameters" tab
- **Sections per provider:**
  - Provider name and icon
  - List of parameters with:
    - Parameter name and description
    - Input field (text, slider, dropdown based on type)
    - Current value
    - Default value shown as placeholder
    - Min/max range display
  - Reset to defaults button
  - Save button
- **UI Examples:**
  ```
  OPENAI PARAMETERS
  ─────────────────
  Temperature: [Slider: 0━━●━━2] 1.0
  Max Tokens: [Input: 2000] (max: 128000)
  Top P: [Slider: 0━━●━━1] 1.0
  Frequency Penalty: [Slider: -2━●━2] 0.0
  ☐ Best Of: [Input: 1]
  Stop Sequences: [Input: ▼] Add sequence
  
  [Reset to Defaults] [Save]
  ```
- **Interactions:**
  - Real-time validation as user types
  - Helpful tooltips on hover
  - Visual indication of non-default values
  - Quick presets (e.g., "Precise", "Creative", "Balanced")
- **Acceptance Criteria:**
  - ✓ All provider params configurable in UI
  - ✓ Sliders for float ranges
  - ✓ Input fields for specific values
  - ✓ Validation feedback shown
  - ✓ Changes persist after save

#### REQ-503-E: Parameter Presets
- **Description:** Save parameter configurations as named presets
- **Preset Structure:**
  ```json
  {
    "name": "Precise Code Generation",
    "description": "Optimal for code generation tasks",
    "provider": "openai",
    "parameters": {
      "temperature": 0.2,
      "max_tokens": 4000,
      "top_p": 1.0
    },
    "created_at": "2025-11-15T10:30:00Z",
    "is_default": false
  }
  ```
- **Built-in Presets:**
  - "Precise" (low temperature, high focus)
  - "Balanced" (default parameters)
  - "Creative" (high temperature, more variety)
  - "Code" (optimized for programming)
  - "Analysis" (long context, detailed output)
- **User-Created Presets:**
  - Save current parameters as named preset
  - Apply preset to current/future sessions
  - Edit preset parameters
  - Delete custom presets
- **Storage:** In project settings or global settings
- **Acceptance Criteria:**
  - ✓ Built-in presets available
  - ✓ Can create custom presets
  - ✓ Can apply presets
  - ✓ Presets persist across sessions

#### REQ-503-F: Dynamic Parameter UI
- **Description:** Generate UI based on provider parameter schema
- **Dynamic Generation:**
  - Read parameter constraints from schema
  - Generate appropriate input controls:
    - Slider for float ranges
    - Integer input for ints with range
    - Checkbox for booleans
    - Dropdown for enums
    - Text area for arrays/multiline
  - Show tooltips from schema descriptions
- **Conditional Display:**
  - Show/hide params based on other values (if available)
  - Disable params that don't apply
  - Group params by category
- **Acceptance Criteria:**
  - ✓ UI generates automatically from schema
  - ✓ Correct input types used
  - ✓ All validation reflected in UI
  - ✓ No hardcoded parameter lists

#### REQ-503-G: Parameter Effects Display
- **Description:** Show estimated effects of parameters
- **Estimated Impacts:**
  - Temperature: Shows "More random" ↔ "More focused"
  - Max Tokens: Shows estimated time/cost impact
  - Top P: Shows "More diverse" ↔ "More consistent"
- **Display Format:**
  - Visual gauge under parameter
  - Textual description
  - Example impact ("Responses will be shorter, faster")
- **Acceptance Criteria:**
  - ✓ Effects clearly explained
  - ✓ Users understand parameter purpose
  - ✓ Descriptive labels provided

#### REQ-503-H: Parameter History and Comparison
- **Description:** Track and compare parameter usage
- **Tracking:**
  - Save parameters used for each message
  - Show parameters in message metadata
  - Compare parameters between messages
- **Comparison:**
  - Side-by-side view of two messages' parameters
  - Diff highlighting of different parameters
  - Insights on how parameters affected output
- **Acceptance Criteria:**
  - ✓ Parameters stored with each message
  - ✓ Can compare two messages' parameters
  - ✓ Differences highlighted

### 2.2 Technical Constraints

- **Parameter Count:** Support up to 20 configurable parameters per provider
- **String Length:** Parameter string values up to 1,000 characters
- **Array Length:** Parameter arrays up to 100 items
- **Float Precision:** 4 decimal places for float parameters
- **Validation Time:** <100ms for parameter validation
- **UI Response:** Parameter changes should show validation within 100ms

---

## 3. Implementation Details

### 3.1 Backend Services

**ProviderParametersService** (`backend/services/provider_parameters_service.py`)

**Key Methods:**
- `get_parameter_schema(provider_id)` - Get parameter constraints
- `validate_parameters(provider_id, params)` - Validate parameter set
- `apply_parameters(provider_id, params, defaults)` - Apply hierarchy
- `resolve_parameters(project_id, session_id)` - Get final parameters
- `save_preset(name, provider_id, params)` - Save as preset
- `get_presets(provider_id)` - List available presets
- `apply_preset(preset_id)` - Apply preset parameters

**Parameter Schema Storage:**
```python
PARAMETER_SCHEMAS = {
    "openai": {
        "temperature": {
            "type": "float",
            "min": 0,
            "max": 2,
            "default": 1.0,
            "description": "What sampling temperature to use..."
        },
        "max_tokens": {
            "type": "int",
            "min": 1,
            "max": 128000,
            "default": None,
            "required": False,
            "description": "The maximum number of tokens..."
        }
    }
}
```

### 3.2 Frontend Components

**ProviderParametersSettings.tsx**
- Tabbed interface per provider
- Dynamic UI generation from schema
- Real-time validation
- Preset management UI
- Reset to defaults button

**ParameterInput.tsx** (Reusable)
- Renders appropriate control based on parameter type
- Shows min/max/default values
- Displays validation errors
- Provides tooltips

### 3.3 API Endpoints

- **GET** `/api/ai-providers/{id}/parameter-schema` - Get constraints
- **GET** `/api/ai-providers/{id}/parameters` - Get current parameters
- **POST** `/api/ai-providers/{id}/parameters/validate` - Validate params
- **PUT** `/api/ai-providers/{id}/parameters` - Save parameters
- **GET** `/api/ai-providers/{id}/presets` - List presets
- **POST** `/api/ai-providers/{id}/presets` - Create preset

---

## 4. Testing Strategy

**Test File:** `tests/unit/test_provider_parameters.py`

- `test_parameter_schema_exists`: Schema defined for all providers
- `test_temperature_validation_openai`: Temperature validated correctly
- `test_temperature_validation_anthropic`: Different constraints per provider
- `test_out_of_range_clamping`: Values clamped to valid range
- `test_required_parameter_validation`: Missing required params caught
- `test_parameter_override_hierarchy`: Override priority works
- `test_preset_save_and_load`: Presets persist correctly
- `test_parameter_with_message`: Parameters saved with message

**Test File:** `tests/integration/test_provider_parameters_api.py`

- `test_get_parameter_schema`: Returns correct schema
- `test_validate_parameters_endpoint`: API validation works
- `test_invalid_parameters_rejected`: Invalid params rejected
- `test_presets_management`: Full preset CRUD works

---

## 5. Dependencies & Relationships

### 5.1 Depends On

| REQ-ID | Title | Reason |
|--------|-------|--------|
| REQ-501 | Multiple provider support | Parameters per provider |
| REQ-502 | API endpoint authentication | Params sent to provider API |
| REQ-308 | Settings page | Parameters UI located here |

### 5.2 Enables / Unblocks

| REQ-ID | Title | How |
|--------|-------|-----|
| REQ-504 | Provider config in .env | Parameters stored in config |
| REQ-518 | Apply provider config | Uses these parameters |

---

## 6. Acceptance Checklist

- [x] Parameter schemas defined for all providers
- [x] Parameters validated against constraints
- [x] Parameters stored at multiple levels
- [x] Override hierarchy works correctly
- [x] Settings UI for parameter configuration
- [x] Parameter presets supported
- [x] Parameters persisted with messages
- [x] Tests passing

---

## Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-15 | Development Team | Initial specification |

---

**Status:** Ready for team use
