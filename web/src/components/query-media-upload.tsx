import message from '@/components/ui/message';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { transformFile2Base64, transformFile2DataUrl } from '@/utils/file-util';
import { Film, ImagePlus, X } from 'lucide-react';
import { ChangeEvent, useRef } from 'react';
import { useTranslation } from 'react-i18next';

export interface IQueryMediaValue {
  kind: 'image' | 'video';
  base64: string;
  fileName: string;
  previewUrl?: string;
}

interface IQueryMediaUploadProps {
  value?: IQueryMediaValue | null;
  onChange: (value: IQueryMediaValue | null) => void;
  disabled?: boolean;
  className?: string;
}

export function QueryMediaUpload({
  value,
  onChange,
  disabled,
  className,
}: IQueryMediaUploadProps) {
  const { t } = useTranslation();
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handlePickFile = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) {
      return;
    }

    try {
      if (file.type.startsWith('image/')) {
        const base64 = await transformFile2Base64(file, 1000);
        onChange({
          kind: 'image',
          base64,
          fileName: file.name,
          previewUrl: base64,
        });
        return;
      }

      if (file.type.startsWith('video/')) {
        const base64 = await transformFile2DataUrl(file);
        onChange({
          kind: 'video',
          base64,
          fileName: file.name,
        });
        return;
      }

      message.error(t('search.mediaTypeError'));
    } catch (_error) {
      message.error(t('search.mediaUploadError'));
    }
  };

  return (
    <div
      className={cn(
        'rounded-xl border border-dashed border-border-button bg-bg-card/70 p-3',
        className,
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*,video/*"
        className="hidden"
        onChange={handlePickFile}
        disabled={disabled}
      />
      <div className="flex flex-wrap items-center gap-3">
        <Button
          type="button"
          variant="outline"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
          className="border-border-button bg-bg-base text-text-primary"
        >
          <ImagePlus className="size-4" />
          {t('search.uploadMedia')}
        </Button>
        {value ? (
          <div className="flex max-w-full items-center gap-3 text-sm text-text-secondary">
            {value.kind === 'image' && value.previewUrl ? (
              <img
                src={value.previewUrl}
                alt={value.fileName}
                className="size-10 rounded-md border border-border-button object-cover"
              />
            ) : (
              <div className="flex size-10 items-center justify-center rounded-md border border-border-button bg-bg-base">
                <Film className="size-4" />
              </div>
            )}
            <span className="max-w-[320px] truncate">
              {(value.kind === 'image'
                ? t('search.selectedImage')
                : t('search.selectedVideo')) + ': ' + value.fileName}
            </span>
            <button
              type="button"
              className="rounded-full p-1 text-text-secondary transition hover:bg-bg-base hover:text-text-primary"
              onClick={() => onChange(null)}
              aria-label={t('search.clearMedia')}
            >
              <X className="size-4" />
            </button>
          </div>
        ) : (
          <span className="text-sm text-text-secondary">
            {t('search.mediaHint')}
          </span>
        )}
      </div>
    </div>
  );
}
