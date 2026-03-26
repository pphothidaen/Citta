# Stage 1: Builder Layer
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production Layer (Zero-Waste)
FROM python:3.11-slim
WORKDIR /app

# คัดลอกเฉพาะไลบรารีที่ติดตั้งแล้วจาก Builder Layer
COPY --from=builder /root/.local /root/.local
COPY main.py .

# อัปเดต PATH ให้ระบบมองเห็น Package ที่ติดตั้งแบบ --user
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]