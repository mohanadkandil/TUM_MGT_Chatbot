import { getServerSession, type NextAuthOptions } from 'next-auth';
import { useSession } from "next-auth/react";
import { redirect, useRouter } from "next/navigation";

// Custom OIDC provider for TUM
const TUMProvider = [
  {
    id: process.env.TUMIDP_ID as string,
    issuer: process.env.TUMIDP_ISSUER as string,
    name: "TUMCHAT",
    type: "oauth",
    wellKnown: process.env.TUMIDP_WELLKNOWN as string,
    clientId: process.env.TUMIDP_CLIENT_ID as string,
    clientSecret: process.env.TUMIDP_CLIENT_SECRET as string,
    authorization: { 
      params: { scope: "openid profile" },
    },
    idToken: true,
    checks: ["pkce", "state"],
    profile(profile: any) {
      console.log("profile: ", profile)
      return {
        id: profile.sub,
        name: profile.name ?? profile.preferred_username,
        email: profile.email,
      };
    },
  },
];

export const authOptions: NextAuthOptions = {
  // @ts-ignore:
  providers: TUMProvider,
  callbacks: {
    async jwt({ token, account }) {
      if (account?.access_token) {
        console.log("Access Token (JWT Callback):", account.access_token);
        token.accessToken = account.access_token;
    
        // Manually fetching user profile -
        const res = await fetch(process.env.TUMIDP_USERINFO as string, {
          headers: {
            Authorization: `Bearer ${account.access_token}`,
          },
        });
    
        const profile = await res.json();
        console.log("Fetched profile:", profile);
    
        // Now map the profile information
        token.preferred_username = profile.preferred_username
        token.given_name = profile.given_name ?? profile.preferred_username;
        token.email = profile.email; 
      }
      return token;
    },
    async session({ session, token }) {
      // Use the token's content to set the session information
      if (session.user) {
        session.user.id = token.preferred_username as string;
        session.user.name = token.given_name as string;
        session.user.email = token.email;
      }
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
};

export async function loginIsRequiredServer() {
  const session = await getServerSession(authOptions);
  if (!session) return redirect("/");
}

