# Cloud Storage Setup Guide

Profile picture uploads require cloud storage configuration. This guide covers both AWS S3 and Cloudflare R2.

## Option 1: AWS S3 Setup

### 1. Create S3 Bucket

1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Click "Create bucket"
3. **Bucket name**: `your-app-profiles` (must be globally unique)
4. **Region**: Choose closest to your users (e.g., `us-east-1`)
5. **Block Public Access**: UNCHECK "Block all public access" (we need public read)
6. Click "Create bucket"

### 2. Configure Bucket Policy

1. Click on your bucket → **Permissions** tab
2. Scroll to **Bucket policy** → Click "Edit"
3. Paste this policy (replace `your-app-profiles` with your bucket name):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-app-profiles/*"
    }
  ]
}
```

4. Click "Save changes"

### 3. Create IAM User for API Access

1. Go to [IAM Console](https://console.aws.amazon.com/iam/)
2. Click "Users" → "Create user"
3. **User name**: `s3-upload-user`
4. Click "Next"
5. **Attach policies**: Select "AmazonS3FullAccess" (or create custom policy below)
6. Click "Next" → "Create user"

**Custom Policy (Recommended - Least Privilege):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::your-app-profiles/*"
    }
  ]
}
```

### 4. Create Access Keys

1. Click on the created user → **Security credentials** tab
2. Scroll to **Access keys** → Click "Create access key"
3. Select "Application running outside AWS"
4. Click "Next" → "Create access key"
5. **SAVE** the Access Key ID and Secret Access Key

### 5. Update .env File

Add these variables to `backend/.env`:

```env
S3_BUCKET_NAME=your-app-profiles
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
S3_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_ENDPOINT_URL=  # Leave empty for AWS S3
S3_PUBLIC_URL=https://your-app-profiles.s3.us-east-1.amazonaws.com
```

---

## Option 2: Cloudflare R2 Setup (Recommended - No Egress Fees)

### 1. Create R2 Bucket

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select your account → **R2** → "Create bucket"
3. **Bucket name**: `your-app-profiles`
4. **Location**: Choose closest region
5. Click "Create bucket"

### 2. Configure Public Access

1. Click on your bucket → **Settings** tab
2. Scroll to **Public access** → Click "Allow Access"
3. Copy the **Public bucket URL** (e.g., `https://pub-xxxxx.r2.dev`)

### 3. Create API Token

1. Go to **R2** → **Overview** → "Manage R2 API Tokens"
2. Click "Create API token"
3. **Token name**: `profile-upload-token`
4. **Permissions**: "Object Read & Write"
5. **Bucket**: Select `your-app-profiles` (or "All buckets")
6. Click "Create API Token"
7. **SAVE** the Access Key ID and Secret Access Key

### 4. Update .env File

Add these variables to `backend/.env`:

```env
S3_BUCKET_NAME=your-app-profiles
S3_REGION=auto
S3_ACCESS_KEY_ID=<your-r2-access-key-id>
S3_SECRET_ACCESS_KEY=<your-r2-secret-access-key>
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
S3_PUBLIC_URL=https://pub-xxxxx.r2.dev
```

**Find your Account ID and Endpoint:**
- Account ID: Dashboard URL → `https://dash.cloudflare.com/<ACCOUNT_ID>/r2`
- Endpoint: R2 → Settings → "S3 API" section

---

## Testing the Upload Endpoint

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 3. Register & Login

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'

# Login (save the token)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

### 4. Upload Profile Picture

```bash
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8000/api/v1/profile/upload-picture \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/image.jpg"
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": null,
  "profile_picture": "https://your-bucket.s3.us-east-1.amazonaws.com/profiles/user-1/abc123.jpg",
  "created_at": "2026-01-07T10:00:00Z"
}
```

### 5. Verify Upload

The `profile_picture` URL should be publicly accessible:
```bash
curl https://your-bucket.s3.us-east-1.amazonaws.com/profiles/user-1/abc123.jpg --output test.jpg
```

---

## Troubleshooting

### Error: "Cloud storage is not configured" (503)

**Cause**: Missing S3 environment variables

**Solution**: Ensure `S3_BUCKET_NAME`, `S3_ACCESS_KEY_ID`, and `S3_SECRET_ACCESS_KEY` are set in `.env`

### Error: "Invalid file type" (400)

**Cause**: Uploading non-image file

**Solution**: Only JPEG, PNG, GIF, WebP allowed

### Error: "File size exceeds maximum of 5MB" (400)

**Cause**: Image too large

**Solution**: Compress or resize image before upload

### Error: "Failed to upload file to cloud storage" (500)

**Possible causes**:
1. Invalid credentials → Check Access Key ID and Secret Key
2. Wrong bucket name → Verify `S3_BUCKET_NAME`
3. Wrong region → Verify `S3_REGION`
4. Wrong endpoint → For R2, ensure `S3_ENDPOINT_URL` is correct
5. Missing permissions → IAM user needs `s3:PutObject` and `s3:PutObjectAcl`

### Images Not Publicly Accessible

**AWS S3**:
- Check bucket policy allows `s3:GetObject` for `Principal: "*"`
- Verify "Block Public Access" settings are OFF

**Cloudflare R2**:
- Enable "Public access" in bucket settings
- Use the correct public URL (not the S3 API endpoint)

---

## Cost Comparison

### AWS S3
- **Storage**: ~$0.023/GB/month
- **PUT requests**: $0.005 per 1,000 requests
- **GET requests**: $0.0004 per 1,000 requests
- **Data transfer OUT**: $0.09/GB (expensive!)

### Cloudflare R2
- **Storage**: $0.015/GB/month
- **Class A operations** (PUT): $4.50 per million
- **Class B operations** (GET): $0.36 per million
- **Data transfer OUT**: **$0** (FREE - no egress fees!)

**Recommendation**: Use Cloudflare R2 for production to avoid egress costs.

---

## Security Best Practices

1. **Never commit credentials** - Use `.env` file (already in `.gitignore`)
2. **Rotate access keys** regularly (every 90 days)
3. **Use least privilege** - IAM policy should only allow upload to profiles bucket
4. **Enable CORS** if uploading from browser:
   ```json
   {
     "AllowedOrigins": ["https://yourapp.com"],
     "AllowedMethods": ["GET", "PUT", "POST"],
     "AllowedHeaders": ["*"],
     "MaxAgeSeconds": 3000
   }
   ```
5. **Scan uploaded files** for malware (consider AWS Lambda + ClamAV)
6. **Set max file size** - Already limited to 5MB in code
7. **Generate unique filenames** - Already using UUID in code

---

## Default Profile Picture

If you want to serve a default image when users haven't uploaded one:

1. Upload a default profile picture to your bucket: `profiles/default/avatar.png`
2. In frontend, check if `profile_picture` is null:
   ```typescript
   const avatarUrl = user.profile_picture || 'https://your-bucket.s3.amazonaws.com/profiles/default/avatar.png';
   ```

---

## Next Steps

Once cloud storage is configured and tested:
1. Proceed to **Phase 2: Frontend Implementation**
2. Update frontend to call upload endpoint
3. Display profile pictures in navbar
4. Add theme toggle
5. Implement history tab and filters
