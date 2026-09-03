# Process Control REST API Contract v1

## 1. Purpose and Scope

This document defines the public REST contract of the Version 2 Backend. It is consumed by the Process Control GUI, the Configurator client, and Robot Framework automated tests.

The API version is independent of the software version. Version 2 software initially exposes API `v1`.

## 2. Base URL and General Rules

- Base URL: `http://pcberry.local:<port>/api/v1`.
- Requests and responses use `application/json` unless an endpoint states otherwise.
- Requests are synchronous. The Backend completes the operation or returns an error/timeout before responding.
- No concurrent REST access is supported. Only one REST request may be active at a time.
- A second request received while another is active shall receive a documented busy response, consistently implemented as `409 Conflict`.
- Clients shall use an HTTP timeout. Backend CAN and logging operations shall also have bounded timeouts.
- Node identifiers use the configured CSN CAN ID and one documented numeric representation.
- Clients use semantic operations; raw CAN IDs and payload layouts are not exposed as the primary API abstraction.

## 3. Common Error Contract

```json
{
	"error": {
		"code": "CAN_TIMEOUT",
		"message": "No response received from node 2047",
		"details": {
			"node_id": 2047,
			"timeout_ms": 2000
		}
	},
	"timestamp": "2026-09-02T12:00:00Z"
}
```

`code` is a stable machine-readable identifier. `message` is diagnostic text. `details` is optional and operation-specific.

| Status | Meaning |
| --- | --- |
| `200 OK` | Synchronous request completed successfully. |
| `201 Created` | A new logging resource was created. |
| `400 Bad Request` | Invalid JSON or field values. |
| `404 Not Found` | Requested node or resource is unknown. |
| `409 Conflict` | Request conflicts with the single-request rule or current node state. |
| `422 Unprocessable Entity` | Request violates a domain rule. |
| `500 Internal Server Error` | Unexpected Backend failure. |
| `503 Service Unavailable` | Backend or required CAN service is unavailable. |
| `504 Gateway Timeout` | Synchronous operation exceeded its timeout. |

## 4. Health

### `GET /health`

Returns the GUI, Backend, and Configurator versions; versions reported by all connected CSNs; Backend/CAN status; and recent Backend-observed errors.

```json
{
	"status": "ok",
	"timestamp": "2026-09-02T12:00:00Z",
	"software": {
		"gui": "2.0.0",
		"backend": "2.0.0",
		"configurator": "2.0.0"
	},
	"backend": {
		"rest_api": "v1",
		"can": {
			"status": "connected",
			"interface": "can0"
		}
	},
	"connected_csn": [
		{
			"node_id": 2047,
			"firmware_version": "1.3.0",
			"hardware_version": "1.0",
			"status": "connected",
			"last_seen": "2026-09-02T11:59:58Z"
		}
	],
	"recent_errors": []
}
```

`recent_errors` contains the last 10 errors by default, ordered newest first. The limit is configurable and may change; clients must not assume that exactly 10 entries are returned. Each entry should include `timestamp`, `code`, `message`, `node_id` when applicable, and `operation` when applicable.

Connected CSN version fields depend on firmware identification data. If a CSN does not report a version, the value is `null` and the version is treated as `unknown`; the Backend must not invent a version.

#### Health status definitions

The top-level `status` describes whether the Backend can provide its advertised service. It is not a direct copy of an individual CSN state.

| Status | Definition | Typical conditions |
| --- | --- | --- |
| `ok` | The Backend is running normally, the REST interface is operational, the CAN adapter is connected and usable, and all CSNs required for the current station operation are reachable with current data. No unresolved condition prevents normal operation. | Backend process is healthy; `can0` is available; expected CSNs have been seen within the configured supervision timeout; no active critical error. |
| `degraded` | The Backend and REST interface are operational, but one or more non-critical capabilities or dependencies are limited. Some operations may fail or return stale/incomplete data, while health and at least part of the advertised service remain available. | One expected CSN is disconnected or stale; a CSN version is unknown; logging is unavailable; non-critical CAN or Backend errors have occurred. |
| `unavailable` | The Backend cannot provide the required service to clients. The health endpoint may still respond with this status, but normal node, configuration, control, or logging operations cannot be completed reliably. | Backend startup failure; REST service cannot reach its required data layer; CAN adapter is missing or unusable for all node operations; a critical internal error blocks service. |

Status evaluation uses the most severe applicable condition: `unavailable` takes precedence over `degraded`, and `degraded` takes precedence over `ok`. A CSN that is not required for the current operation does not by itself make the overall Backend unavailable. The Backend shall include enough component information, such as CAN status, connected CSNs, and recent errors, for clients to determine why the status was assigned.

## 5. Runtime Values

### `GET /nodes/{node_id}/values`

Returns the latest known runtime snapshot. The implementation shall document whether this is cached or fetched from a fresh CAN frame. The timestamp identifies the age of the data.

```json
{
	"node_id": 2047,
	"value": 120,
	"min_value": -100,
	"max_value": 500,
	"set_value": 100,
	"default_value": 0,
	"state": "running",
	"error_code": 0,
	"timestamp": "2026-09-02T12:00:00Z"
}
```

## 6. Control

Control is not yet implemented in API v1. The endpoint `POST /nodes/{node_id}/control` is reserved for a future API revision and shall not be called by the GUI, Configurator, or automated REST contract tests.

## 7. Configuration

### `POST /nodes/{node_id}/setup`

Enters setup mode and returns the configuration when the synchronous setup/read operation completes.

### `GET /nodes/{node_id}/configuration`

Returns the latest known configuration.

### `PUT /nodes/{node_id}/configuration`

Validates and writes the complete configuration synchronously.

Configuration JSON should include:

```text
name, unit, value, value_set, value_default, value_min, value_max,
value_offset, value_multiplier, update_rate_ms, node_type, can_id,
last_error_code
```

Values outside the CSN protocol range shall be rejected before CAN transmission.

### `POST /nodes/{node_id}/setup/complete`

Stores the configuration and leaves setup mode synchronously.

## 8. Logging

### `POST /logging/start`

Starts logging synchronously. The caller may customize the filename.

Request:

```json
{
	"filename": "test-run-001.csv"
}
```

The Backend owns the final path and applies its configured log directory and filename-safety policy. A filename must not escape the permitted directory or overwrite protected files.

### `POST /logging/stop`

Stops logging synchronously and confirms that the file is closed.

### `GET /logging/status`

Returns the logging state, active filename, start time, and records written.

```json
{
	"state": "active",
	"filename": "/var/log/process-control/test-run-001.csv",
	"started_at": "2026-09-02T12:00:00Z",
	"records_written": 18
}
```

Valid logging states are `inactive`, `starting`, `active`, `stopping`, and `error`.

## 9. Client Responsibilities

- The GUI and Configurator use this API for all Backend operations.
- Robot Framework uses this API for CSN data, configuration, control, and logging.
- Clients check `/health` before a test or operational session.
- Clients handle `409`, timeout, CAN, and Backend errors explicitly.
- Clients do not access Backend memory, files, or internal modules directly.

## 10. Compatibility

The API remains `v1` for backward-compatible additions. A new API version is required for incompatible request, response, or semantic changes. API versioning is independent of GUI, Backend, Configurator, and CSN software versions.
