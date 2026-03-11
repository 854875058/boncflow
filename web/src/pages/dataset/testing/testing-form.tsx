'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm, useWatch } from 'react-hook-form';
import { z } from 'zod';

import { CrossLanguageFormField } from '@/components/cross-language-form-field';
import { FormContainer } from '@/components/form-container';
import {
  MetadataFilter,
  MetadataFilterSchema,
} from '@/components/metadata-filter';
import {
  IQueryMediaValue,
  QueryMediaUpload,
} from '@/components/query-media-upload';
import {
  RerankFormFields,
  initialTopKValue,
  topKSchema,
} from '@/components/rerank';
import {
  SimilaritySliderFormField,
  initialSimilarityThresholdValue,
  initialVectorSimilarityWeightValue,
  similarityThresholdSchema,
  vectorSimilarityWeightSchema,
} from '@/components/similarity-slider';
import { ButtonLoading } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from '@/components/ui/form';
import { Textarea } from '@/components/ui/textarea';
import { UseKnowledgeGraphFormField } from '@/components/use-knowledge-graph-item';
import { useTestRetrieval } from '@/hooks/use-knowledge-request';
import { trim } from 'lodash';
import { Send } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams } from 'umi';

type TestingFormProps = Pick<
  ReturnType<typeof useTestRetrieval>,
  'loading' | 'refetch' | 'setValues'
>;

export default function TestingForm({
  loading,
  refetch,
  setValues,
}: TestingFormProps) {
  const { t } = useTranslation();
  const { id } = useParams();
  const knowledgeBaseId = id;

  const formSchema = z
    .object({
      question: z.string().optional(),
      image_base64: z.string().optional(),
      video_base64: z.string().optional(),
      media_filename: z.string().optional(),
      ...similarityThresholdSchema,
      ...vectorSimilarityWeightSchema,
      ...topKSchema,
      use_kg: z.boolean().optional(),
      kb_ids: z.array(z.string()).optional(),
      ...MetadataFilterSchema,
    })
    .superRefine((value, ctx) => {
      if (
        !trim(value.question || '') &&
        !value.image_base64 &&
        !value.video_base64
      ) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: t('knowledgeDetails.testTextPlaceholder'),
          path: ['question'],
        });
      }
    });

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      question: '',
      image_base64: '',
      video_base64: '',
      media_filename: '',
      ...initialSimilarityThresholdValue,
      ...initialVectorSimilarityWeightValue,
      ...initialTopKValue,
      use_kg: false,
      kb_ids: [knowledgeBaseId],
    },
  });
  const [queryMedia, setQueryMedia] = useState<IQueryMediaValue | null>(null);

  const question = form.watch('question');

  const values = useWatch({ control: form.control });

  useEffect(() => {
    setValues(values as Required<z.infer<typeof formSchema>>);
  }, [setValues, values]);

  useEffect(() => {
    form.setValue(
      'image_base64',
      queryMedia?.kind === 'image' ? queryMedia.base64 : '',
      { shouldValidate: true },
    );
    form.setValue(
      'video_base64',
      queryMedia?.kind === 'video' ? queryMedia.base64 : '',
      { shouldValidate: true },
    );
    form.setValue('media_filename', queryMedia?.fileName || '');
  }, [form, queryMedia]);

  function onSubmit() {
    refetch();
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormContainer className="p-10">
          <SimilaritySliderFormField
            isTooltipShown={true}
          ></SimilaritySliderFormField>
          <RerankFormFields></RerankFormFields>
          <UseKnowledgeGraphFormField name="use_kg"></UseKnowledgeGraphFormField>
          <CrossLanguageFormField
            name={'cross_languages'}
          ></CrossLanguageFormField>
          <MetadataFilter prefix=""></MetadataFilter>
        </FormContainer>
        <FormField
          control={form.control}
          name="question"
          render={({ field }) => (
            <FormItem>
              {/* <FormLabel>{t('knowledgeDetails.testText')}</FormLabel> */}
              <FormControl>
                <Textarea {...field}></Textarea>
              </FormControl>

              <FormMessage />
            </FormItem>
          )}
        />
        <QueryMediaUpload
          value={queryMedia}
          onChange={setQueryMedia}
          disabled={loading}
        />
        <div className="flex justify-end">
          <ButtonLoading
            type="submit"
            disabled={!trim(question || '') && !queryMedia?.base64}
            loading={loading}
          >
            {/* {!loading && <CirclePlay />} */}
            {t('knowledgeDetails.testingLabel')}
            <Send />
          </ButtonLoading>
        </div>
      </form>
    </Form>
  );
}
