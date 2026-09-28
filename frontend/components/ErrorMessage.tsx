export default function ErrorMessage({
  message,
  action,
}: {
  message: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-4 text-red-800">
      <p className="font-medium">Error</p>
      <p className="mt-1 text-sm">{message}</p>
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}
