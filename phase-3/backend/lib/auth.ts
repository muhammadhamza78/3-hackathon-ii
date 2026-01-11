import { compare } from "bcryptjs";
import jwt from "jsonwebtoken";
import { prisma } from "./prisma";

if (!process.env.JWT_SECRET) {
  throw new Error("JWT_SECRET must be set in .env");
}
export const auth = {
  login: async ({ email, password }: { email: string; password: string }) => {
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) throw new Error("Invalid credentials");

    const valid = await compare(password, user.password);
    if (!valid) throw new Error("Invalid credentials");

    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET!, { expiresIn: "1h" });

return {
  access_token: token,
  token_type: "Bearer",
  expires_in: 3600,
  user: {
    id: user.id,
    email: user.email,
    name: user.name || "",          // ← safe fallback
    profile_picture: user.profile_picture || null,
  },
};

  },

  




  session: async ({ token }: { token: string }) => {
    try {
      const payload = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };
      const user = await prisma.user.findUnique({ where: { id: payload.userId } });
      return user || null;
    } catch {
      return null;
    }
  },

  logout: async () => ({ success: true }),
};









