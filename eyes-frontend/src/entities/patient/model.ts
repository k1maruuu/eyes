export type PatientStatus =
    | "NEW"
    | "IN_PREPARATION"
    | "READY_FOR_REVIEW"
    | "REVISION_REQUIRED"
    | "APPROVED"
    | "SURGERY_SCHEDULED"
    | "SURGERY_DONE";

export type Patient = {
    id: number;
    organization_id: number | null;

    fio: string;
    birth_date: string | null; // date
    sex: string | null;

    snils: string | null;
    polis: string | null;
    passport: string | null;

    status: PatientStatus;

    diagnosis_text: string | null;
    operation_type: string | null;

    fhir_id: string | null;
    fhir_resource_json: Record<string, any> | null;
    external_system_id: string | null;

    created_at: string; // datetime
    updated_at: string; // datetime
};