# Database Schema

## Tables

### users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| name | TEXT | User's full name |
| roll | TEXT | Roll/ID number |
| encoding | BLOB | Face recognition encoding (pickled) |
| photo | TEXT | Path to registered face photo |

### attendance
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PRIMARY KEY | Auto-increment ID |
| user_id | INTEGER | Foreign key to users.id |
| timestamp | TEXT | DateTime of attendance (YYYY-MM-DD HH:MM:SS) |
| status | TEXT | "IN" or "OUT" |
| photo | TEXT | Path to attendance photo |

## Database
- **Path**: `database/attendance.db`
- **Type**: SQLite
