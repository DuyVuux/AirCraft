# 🛠️ Development Guide

Hướng dẫn phát triển cho dự án Aircraft Web.

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm hoặc yarn
- Git

### Setup Project

```bash
# Clone repository
git clone <repository-url>
cd aircraft-web

# Setup frontend
cd frontend
npm install
npm run dev

# Setup backend (optional)
cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 📁 Project Structure

Xem [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) để biết chi tiết cấu trúc dự án.

## 🔧 Development Workflow

### 1. Tạo Component mới

```typescript
// src/components/MyComponent.tsx
import React from 'react';

interface MyComponentProps {
  // Props definition
}

export const MyComponent: React.FC<MyComponentProps> = (props) => {
  return (
    <div>
      {/* Component content */}
    </div>
  );
};
```

### 2. Tạo Hook mới

```typescript
// src/hooks/useMyHook.ts
import { useState, useEffect } from 'react';

export const useMyHook = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Hook logic
  }, []);

  return { data };
};
```

### 3. Tạo Service mới

```typescript
// src/services/myService.ts
import { api } from './api';

export const myService = {
  async getData() {
    return await api.get('/endpoint');
  },
  
  async postData(data: any) {
    return await api.post('/endpoint', data);
  }
};
```

## 🧪 Testing

### Unit Tests

```bash
npm run test
```

### Integration Tests

```bash
npm run test:integration
```

### E2E Tests

```bash
npm run test:e2e
```

## 📝 Code Style

### TypeScript
- Sử dụng TypeScript strict mode
- Định nghĩa types/interfaces rõ ràng
- Tránh `any` type

### React
- Sử dụng functional components
- Sử dụng hooks thay vì class components
- Props interface phải được định nghĩa rõ ràng

### Naming Conventions
- Components: PascalCase (ví dụ: `MyComponent.tsx`)
- Hooks: camelCase với prefix `use` (ví dụ: `useMyHook.ts`)
- Utils: camelCase (ví dụ: `myUtil.ts`)
- Types: PascalCase (ví dụ: `MyType.ts`)

## 🔍 Debugging

### Frontend
- Sử dụng React DevTools
- Console.log cho debugging
- Breakpoints trong browser DevTools

### Backend
- Sử dụng FastAPI auto-reload
- Logging với Python logging module
- Debugger trong IDE

## 📦 Build & Deploy

### Build Frontend

```bash
cd frontend
npm run build
```

### Build Backend

```bash
cd backend
# No build needed for Python
```

### Deploy

Xem deployment documentation trong `docs/deployment.md`

## 🐛 Common Issues

### Issue 1: CSV parsing fails
**Solution:** Kiểm tra encoding file (UTF-8)

### Issue 2: JSON validation fails
**Solution:** Kiểm tra schema trong `src/utils/jsonValidator.ts`

### Issue 3: GPS coordinates invalid
**Solution:** Validate longitude (-180 đến 180) và latitude (-90 đến 90)

## 📚 Resources

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite Documentation](https://vitejs.dev/)

