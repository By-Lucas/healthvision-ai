import { useId, useRef, useState } from 'react';

interface DropzoneProps {
  onFile: (file: File) => void;
  disabled?: boolean;
}

export function Dropzone({ onFile, disabled }: DropzoneProps) {
  const inputId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  function handleFiles(files: FileList | null) {
    if (files && files.length > 0) onFile(files[0]);
  }

  return (
    <label
      htmlFor={inputId}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
      className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-6 py-12 text-center transition ${
        dragging
          ? 'border-brand-500 bg-brand-50'
          : 'border-slate-300 bg-white hover:border-brand-400'
      } ${disabled ? 'pointer-events-none opacity-60' : ''}`}
    >
      <div className="text-3xl">📤</div>
      <p className="font-medium text-slate-700">
        Drag & drop a chest X-ray, or click to browse
      </p>
      <p className="text-sm text-slate-400">JPG, JPEG or PNG · up to 10 MB</p>
      <input
        id={inputId}
        ref={inputRef}
        type="file"
        accept=".jpg,.jpeg,.png,image/jpeg,image/png"
        className="hidden"
        data-testid="file-input"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </label>
  );
}
