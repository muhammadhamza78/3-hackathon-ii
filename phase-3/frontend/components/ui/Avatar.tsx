"use client";

interface AvatarProps {
  name: string;
  profilePicture?: string | null;
  size?: "sm" | "md" | "lg";
}

export default function Avatar({ name, profilePicture, size = "md" }: AvatarProps) {
  const sizeClasses = {
    sm: "w-8 h-8 text-sm",
    md: "w-10 h-10 text-base",
    lg: "w-16 h-16 text-2xl",
  };

  // Get first letter of name or email
  const getInitial = () => {
    if (!name) return "?";
    return name.charAt(0).toUpperCase();
  };

  // Generate a consistent color based on name
  const getBackgroundColor = () => {
    if (!name) return "bg-gray-400";

    const colors = [
      "bg-orange-500",
      "bg-blue-500",
      "bg-green-500",
      "bg-purple-500",
      "bg-pink-500",
      "bg-yellow-500",
      "bg-indigo-500",
      "bg-red-500",
    ];

    const charCode = name.charCodeAt(0);
    return colors[charCode % colors.length];
  };

  if (profilePicture) {
    return (
      <div className={`${sizeClasses[size]} rounded-full overflow-hidden flex-shrink-0`}>
        <img
          src={profilePicture}
          alt={name}
          className="w-full h-full object-cover"
        />
      </div>
    );
  }

  return (
    <div
      className={`${sizeClasses[size]} ${getBackgroundColor()} rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0`}
    >
      {getInitial()}
    </div>
  );
}
