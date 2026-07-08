import { useCallback, useEffect, useRef, useState } from "react";
import { Gantt, Willow, type ITask } from "@svar-ui/react-gantt";
import { Locale } from "@svar-ui/react-core";
import "@svar-ui/react-gantt/all.css";
import { usePersistedTasks } from "@/hook/use-persisted-tasks";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import ChatPanel from "@/components/widgets/chat-panel";

type TaskWithAssignee = ITask & {
  assignee?: string;
};

const API_URL = import.meta.env.VITE_API_URL;

const USERS = [
  "Алексей",
  "Мария",
  "Иван",
  "Ольга",
];

export default function GanttChart() {

  const apiRef = useRef<any>(null);
  const isResizing = useRef(false);

  const [tasks, setTasks] =
    usePersistedTasks<ITask[]>([]);

  const [selectedTask, setSelectedTask] =
    useState<TaskWithAssignee | null>(null);

  const [editText, setEditText] =
    useState("");

  const [editAssignee, setEditAssignee] =
    useState("");

  const [chatWidth, setChatWidth] =
    useState(320);

  const [loading, setLoading] =
    useState(true);


  const normalizeTasks = (items: any[]) => {

    return items
      .filter(Boolean)
      .map((t: any) => ({
        id: t.id,

        text: String(
          t.text ?? "Без названия"
        ),

        type:
          t.type ??
          "task",

        start:
          t.start
            ? new Date(t.start)
            : new Date(),

        duration:
          Number(t.duration) || 1,

        progress:
          Number(t.progress) || 0,

        open:
          Boolean(t.open),

        parent:
          t.parent ?? null,

        assignee:
          t.assignee ?? "",

      }))
      .filter(
        (t: any) => t.id
      );
  };


  const loadTasks = useCallback(async () => {

    try {

      setLoading(true);

      const res = await fetch(
        `${API_URL}/tasks`
      );

      const data = await res.json();


      const rawTasks =
        Array.isArray(data?.tasks)
          ? data.tasks
          : Array.isArray(data)
          ? data
          : [];


      setTasks(
        normalizeTasks(rawTasks)
      );


    } catch(error) {

      console.error(
        error
      );

    } finally {

      setLoading(false);

    }

  }, [setTasks]);


  useEffect(() => {

    const saved =
      localStorage.getItem(
        "gantt-tasks"
      );


    if (
      !saved ||
      saved === "[]"
    ) {

      loadTasks();

    } else {

      setLoading(false);

    }

  }, [loadTasks]);


  const init = useCallback((api:any)=>{

    if(apiRef.current){
      return;
    }


    apiRef.current = api;


    api.on(
      "select-task",
      ({id}:any)=>{

        if(!id){

          setSelectedTask(null);

          return;
        }


        const task =
          api.getTask?.(id);


        if(task){

          setSelectedTask(task);

          setEditText(
            task.text ?? ""
          );

          setEditAssignee(
            task.assignee ?? ""
          );

        }

      }
    );


    api.on(
      "update-task",
      ({
        id,
        task:updated
      }:any)=>{

        setTasks(prev =>
          prev.map(t =>
            t.id === id
              ? {
                  ...t,
                  ...updated
                }
              : t
          )
        );

      }
    );


    api.on(
      "add-task",
      ({task}:any)=>{

        setTasks(prev=>[
          ...prev,
          {
            ...task,
            start:
              task.start
                ? new Date(task.start)
                : new Date()
          }
        ]);

      }
    );


  },[setTasks]);


  useEffect(()=>{

    const handleExcelUpload =
      async(event:Event)=>{

        const file =
          (event as CustomEvent).detail;


        if(!file){
          return;
        }


        const formData =
          new FormData();


        formData.append(
          "file",
          file
        );


        try {


          const response =
            await fetch(
              `${API_URL}/upload-excel`,
              {
                method:"POST",
                body:formData
              }
            );


          const data =
            await response.json();


          const imported =
            Array.isArray(data?.tasks)
              ? data.tasks
              : [];


          setTasks(
            normalizeTasks(imported)
          );


        } catch(error){

          console.error(
            error
          );

        }


      };


    window.addEventListener(
      "excel-upload",
      handleExcelUpload
    );


    return ()=>{

      window.removeEventListener(
        "excel-upload",
        handleExcelUpload
      );

    };


  },[setTasks]);

	  useEffect(() => {

    const handler = (event: Event) => {

      const command =
        (event as CustomEvent).detail;
				console.log("GANTT RECEIVED COMMAND:", command);

				console.log("========== AI COMMAND ==========");
		    console.log(command);
		    console.log("ACTION:", command?.action);
		    console.log("DATA:", command?.data);

      if (!command?.action) {
        return;
      }


      switch (command.action) {


        case "create_task": {

          const task =
            command.data?.task;


          if (!task) {
            return;
          }


          setTasks(prev => [
            ...prev,
            {
              id: task.id,

              text:
                task.text ??
                "Без названия",

              type: "task",

              start:
                command.data.start
                  ? new Date(
                      command.data.start
                    )
                  : new Date(),

              duration:
                task.duration ?? 1,

              progress:
                task.progress ?? 0,

              parent:
                task.parent ?? null,

              open: false,

              assignee:
                task.assignee ?? "",
            }
          ]);


          break;
        }


        case "update_task": {

          const id =
            command.data?.id ??
            command.data?.task?.id;


          if (!id) {
            return;
          }


          setTasks(prev =>
            prev.map(task =>
              task.id === id
                ? {
                    ...task,
                    ...(command.data.changes ?? {})
                  }
                : task
            )
          );


          break;
        }


        case "delete_task": {

  const id =
    command.data?.id ??
    command.data?.task?.id;


  console.log("DELETE ID:", id);


  setTasks(prev => {

    console.log("BEFORE DELETE:", prev);


    const updated = prev.filter(
      task => String(task.id) !== String(id)
    );


    console.log("AFTER DELETE:", updated);


    return updated;

  });


  break;
}

      }

    };


    window.addEventListener(
      "gantt-command",
      handler
    );


    return () => {

      window.removeEventListener(
        "gantt-command",
        handler
      );

    };


  }, [setTasks]);


  const saveTask = () => {

    if (
      !selectedTask?.id ||
      !apiRef.current
    ) {
      return;
    }


    apiRef.current.exec(
      "update-task",
      {
        id: selectedTask.id,

        task:{
          text: editText,

          assignee:
            editAssignee,
        }
      }
    );


    setSelectedTask(null);

  };


  useEffect(()=>{

    const onMove =
      (e:MouseEvent)=>{

        if(
          !isResizing.current
        ){
          return;
        }


        const newWidth =
          window.innerWidth -
          e.clientX;


        if(
          newWidth > 240 &&
          newWidth < 600
        ){

          setChatWidth(
            newWidth
          );

        }

      };


    const stop = ()=>{
      isResizing.current = false;
    };


    window.addEventListener(
      "mousemove",
      onMove
    );


    window.addEventListener(
      "mouseup",
      stop
    );


    return ()=>{

      window.removeEventListener(
        "mousemove",
        onMove
      );


      window.removeEventListener(
        "mouseup",
        stop
      );

    };


  },[]);



  if(loading){

    return (
      <div className="flex h-screen w-screen items-center justify-center">
        Загрузка...
      </div>
    );

  }


  return (

    <div className="flex w-screen h-screen overflow-hidden">


      <div className="flex-1 min-w-0">


        <Willow>

          <Locale
            words={{
              gantt:{
                "New task":
                  "Новая задача",

                "Task name":
                  "Название задачи",

                "Start date":
                  "Дата начала",

                Duration:
                  "Длительность",
              }
            }}
          >

            <Gantt
              init={init}
              tasks={tasks || []}
              links={[]}
            />


          </Locale>


        </Willow>


      </div>



      <div
        onMouseDown={()=>{
          isResizing.current = true;
        }}
        className="w-1 cursor-col-resize bg-gray-200 hover:bg-gray-300"
      />



      <ChatPanel
        width={chatWidth}
        tasks={tasks}
        selectedTask={selectedTask}
      />



      <Dialog
        open={!!selectedTask}
        onOpenChange={(o)=>
          !o &&
          setSelectedTask(null)
        }
      >

        <DialogContent className="sm:max-w-[420px]">


          <DialogHeader>

            <DialogTitle>
              Редактирование задачи
            </DialogTitle>

          </DialogHeader>



          {selectedTask && (

            <div className="space-y-4 pt-2">


              <input
                value={editText}
                onChange={(e)=>
                  setEditText(
                    e.target.value
                  )
                }
                className="w-full border rounded-md px-3 py-2"
              />



              <select
                value={editAssignee}
                onChange={(e)=>
                  setEditAssignee(
                    e.target.value
                  )
                }
                className="w-full border rounded-md px-3 py-2"
              >

                <option value="">
                  Без исполнителя
                </option>


                {USERS.map(u=>(

                  <option
                    key={u}
                    value={u}
                  >
                    {u}
                  </option>

                ))}


              </select>



              <button
                onClick={saveTask}
                className="w-full bg-blue-600 text-white py-2 rounded-md"
              >
                Сохранить
              </button>


            </div>

          )}


        </DialogContent>


      </Dialog>


    </div>

  );

}